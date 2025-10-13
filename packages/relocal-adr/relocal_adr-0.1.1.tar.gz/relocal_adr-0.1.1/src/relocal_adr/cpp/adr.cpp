#include "adr.h"

#include <pcl/filters/voxel_grid.h>

#include <execution>
#include <thread>

template <typename T>
bool is_normal_close(const Eigen::Matrix<T, 3, 1> &a,
                     const Eigen::Matrix<T, 3, 1> &b, double thre) {
  bool ret = false;
  auto normal_diff = a - b;
  auto normal_add = a + b;

  if (normal_diff.norm() < thre || normal_add.norm() < thre) {
    ret = true;
  }
  return ret;
}

void down_sample(pcl::PointCloud<pcl::PointXYZI>::Ptr pl_feat,
                 double voxel_size) {
  pcl::VoxelGrid<pcl::PointXYZI> sor;
  sor.setInputCloud(pl_feat);
  sor.setLeafSize(voxel_size, voxel_size, voxel_size);
  sor.filter(*pl_feat);
}

void down_sampling_voxel(pcl::PointCloud<pcl::PointXYZI> &pl_feat,
                         double voxel_size) {
  struct local_voxel_t {
    float xyz[3];
    float intensity;
    int count = 0;
  };

  int intensity = rand() % 255;
  if (voxel_size < 0.01) {
    return;
  }
  std::unordered_map<voxel_loc_t, local_voxel_t> voxel_map;
  uint plsize = pl_feat.size();

  for (uint i = 0; i < plsize; i++) {
    pcl::PointXYZI &p_c = pl_feat[i];
    float loc_xyz[3];
    for (int j = 0; j < 3; j++) {
      loc_xyz[j] = p_c.data[j] / voxel_size;

      if (loc_xyz[j] < 0) {
        loc_xyz[j] -= 1.0;
      }
    }

    voxel_loc_t position((int64_t)loc_xyz[0], (int64_t)loc_xyz[1],
                         (int64_t)loc_xyz[2]);
    auto iter = voxel_map.find(position);

    if (iter != voxel_map.end()) {
      iter->second.xyz[0] += p_c.x;
      iter->second.xyz[1] += p_c.y;
      iter->second.xyz[2] += p_c.z;
      iter->second.intensity += p_c.intensity;
      iter->second.count++;
    } else {
      local_voxel_t anp;
      anp.xyz[0] = p_c.x;
      anp.xyz[1] = p_c.y;
      anp.xyz[2] = p_c.z;
      anp.intensity = p_c.intensity;
      anp.count = 1;
      voxel_map[position] = anp;
    }
  }
  plsize = voxel_map.size();
  pl_feat.clear();
  pl_feat.resize(plsize);

  uint i = 0;
  for (auto iter = voxel_map.begin(); iter != voxel_map.end(); ++iter) {
    pl_feat[i].x = iter->second.xyz[0] / iter->second.count;
    pl_feat[i].y = iter->second.xyz[1] / iter->second.count;
    pl_feat[i].z = iter->second.xyz[2] / iter->second.count;
    pl_feat[i].intensity = iter->second.intensity / iter->second.count;
    i++;
  }
}

desc_t::const_vec_ptr adr_manager_t::GenerateSTDescs(
    pcl::PointCloud<pcl::PointXYZI>::Ptr &input_cloud) {

  voxel_map_t voxel_map;
  to_voxel_map(input_cloud, voxel_map);

  std::vector<voxel_map_t::value_type> planes;
  extract_plane_voxel(voxel_map, planes);
  plane_cloud_vec_.emplace_back(voxel_to_plane_cloud(planes));

  build_connection(voxel_map, planes);

  auto features = extract_img_features(voxel_map);
  corner_cloud_vec_.push_back(features);

  return build_stdesc(features);
}


double flatness(Eigen::Matrix3Xd normals) {
  double rbf_sigma = 0.1;
  static auto rbf = [rbf_sigma](double x) {
    return std::exp(-(x * x) / (2 * rbf_sigma * rbf_sigma));
  };

  Eigen::Vector3d center = normals.rowwise().mean();
  center /= center.norm();
  Eigen::VectorXd signs = (normals.transpose() * center).array().sign();
  normals = normals * signs.asDiagonal();

  Eigen::MatrixXd cos_thetas = normals.transpose() * normals;
  cos_thetas = cos_thetas.cwiseMin(1.0).cwiseMax(-1.0);
  auto thetas = cos_thetas.array().acos();
  Eigen::MatrixXd weights = thetas.array().unaryExpr(rbf);
  Eigen::Matrix3d cov = normals * weights * normals.transpose();
  Eigen::SelfAdjointEigenSolver<Eigen::Matrix3d> es(cov);
  Eigen::Matrix3cd evecs = es.eigenvectors();
  Eigen::Vector3cd evals = es.eigenvalues();

  if((evals.real().maxCoeff() + 1e-3) / (evals.real().minCoeff() + 1e-3) < 10.0) {
    return 0.0;
  }

  Eigen::Vector3d normal = evecs.real().col(2);
  normal *= (normal.dot(normals.rowwise().mean()) > 0.0) ? 1.0 : -1.0;
  Eigen::MatrixXd cos_errs = normals.transpose() * normal;
  cos_errs = cos_errs.cwiseMin(1.0).cwiseMax(-1.0);
  Eigen::VectorXd errs = cos_errs.array().acos();
  auto rmse = std::sqrt((errs.array() * errs.array()).mean());
  return 1.0 / (rmse + 1.0);
}


void adr_manager_t::SearchLoop(
    desc_t::const_vec_ptr stds_vec, std::pair<int, double> &loop_result,
    std::pair<Eigen::Vector3d, Eigen::Matrix3d> &loop_transform,
    match_list_t &loop_std_pair) {
  if (stds_vec->size() == 0) {
    loop_result = std::pair<int, double>(-1, 0);
    return;
  }
  auto t1 = std::chrono::high_resolution_clock::now();
  auto candidate_matcher_vec = build_match_frame(stds_vec);

  auto t2 = std::chrono::high_resolution_clock::now();
  double best_score = 0;
  unsigned int best_candidate_id = -1;
  unsigned int triggle_candidate = -1;
  std::pair<Eigen::Vector3d, Eigen::Matrix3d> best_transform;
  match_list_t best_sucess_match_vec;
  for (size_t i = 0; i < candidate_matcher_vec->size(); i++) {
    double penalty = 0.0;
    auto &match_vec = candidate_matcher_vec->at(i);
    match_info_t best_info = find_best_transform(match_vec);
    if (best_info.size() < 4) {
      continue;
    } 
    else if (best_info.size() < 10) {
      size_t normal_sz = best_info.matches->size() * 3;
      Eigen::Matrix3Xd key_normals{3, normal_sz};
      Eigen::Matrix3Xd loop_normals{3, normal_sz};
      for(size_t j = 0; j < best_info.size(); j++) {
        auto& match = best_info.matches->at(j);
        key_normals.col(j * 3 + 0) = match.first->normals[0];
        key_normals.col(j * 3 + 1) = match.first->normals[1];
        key_normals.col(j * 3 + 2) = match.first->normals[2];
        loop_normals.col(j * 3 + 0) = match.second->normals[0];
        loop_normals.col(j * 3 + 1) = match.second->normals[1];
        loop_normals.col(j * 3 + 2) = match.second->normals[2];
      }
      
      double key_flatness = flatness(key_normals);
      double loop_flatness = flatness(loop_normals);
      double penalty_matches = 1.0 - (best_info.size() - 4.0) / 5.0;
      double penalty_flatness = 0.5 * key_flatness + 0.5 * loop_flatness;
      double penalty_alpha = 0.8;
      penalty = penalty_matches * (1 - penalty_alpha) + penalty_flatness * penalty_alpha;
      penalty *= 0.5;
    }

    double verify_score = evalute_transform(
        plane_cloud_vec_[match_vec.match_id.first],
        plane_cloud_vec_[match_vec.match_id.second], best_info.trans);
    
    verify_score = std::max(0.0, verify_score - penalty);
    if (verify_score > best_score) {
      best_score = verify_score;
      best_candidate_id = match_vec.match_id.second;
      best_transform = std::make_pair(best_info.trans.translation(),
                                      best_info.trans.linear());
      best_sucess_match_vec.swap(*best_info.matches);
      triggle_candidate = i;
    }
  }
  auto t3 = std::chrono::high_resolution_clock::now();


  loop_result = std::pair<int, double>(best_candidate_id, best_score);
  loop_transform = best_transform;
  loop_std_pair = best_sucess_match_vec;
  return;
}

void adr_manager_t::AddSTDescs(const desc_t::const_vec_ptr stds_vec) {
  current_frame_id_++;
  for (auto single_std : *stds_vec) {
    stdesc_loc_t position;

    position.x = (int)(single_std->sides[0] + 0.5);
    position.y = (int)(single_std->sides[1] + 0.5);
    position.z = (int)(single_std->sides[2] + 0.5);
    position.a = (int)(single_std->angles[0]);
    position.b = (int)(single_std->angles[1]);
    position.c = (int)(single_std->angles[2]);
    auto iter = data_base_.find(position);
    if (iter != data_base_.end()) {
      data_base_[position]->push_back(single_std);
    } else {
      auto descriptor_vec = std::make_shared<desc_t::const_vec_t>();
      descriptor_vec->push_back(single_std);
      data_base_[position] = descriptor_vec;
    }
  }
  return;
}

void adr_manager_t::to_voxel_map(
    const pcl::PointCloud<pcl::PointXYZI>::Ptr &input_cloud,
    voxel_map_t &voxel_map) const {
  for (const auto &p : *input_cloud) {
    voxel_loc_t loc{int64_t(p.x / config_setting_.voxel_size_) - (p.x < 0),
                    int64_t(p.y / config_setting_.voxel_size_) - (p.y < 0),
                    int64_t(p.z / config_setting_.voxel_size_) - (p.z < 0)};
    if (voxel_map.find(loc) == voxel_map.end()) {
      auto voxel = std::make_shared<voxel_t>();
      voxel->points.reserve(100);
      voxel_map[loc] = voxel;
    }
    voxel_map[loc]->points.push_back(p.getVector3fMap().cast<double>());
  }
}

void adr_manager_t::extract_plane_voxel(
    voxel_map_t &voxel_map,
    std::vector<voxel_map_t::value_type> &planes) const {
  std::vector<voxel_map_t::value_type> voxel_vec;
  voxel_vec.reserve(voxel_map.size());
  std::copy_if(voxel_map.begin(), voxel_map.end(),
               std::back_inserter(voxel_vec), [&](const auto &pair) {
                 return pair.second->points.size() >
                        config_setting_.voxel_init_num_;
               });

  std::for_each(std::execution::par_unseq, voxel_vec.begin(), voxel_vec.end(),
                [&](auto &pair) {
                  auto &voxel = pair.second;
                  voxel->plane = extract_plane_from_points(voxel->points);
                });

  planes.reserve(voxel_vec.size());
  std::copy_if(voxel_vec.begin(), voxel_vec.end(), std::back_inserter(planes),
               [](const auto &voxel) { return voxel.second->plane.is_plane; });
}

plane_t adr_manager_t::extract_plane_from_points(
    const std::vector<Eigen::Vector3d> &points) const {
  plane_t plane;
  plane.cov = Eigen::Matrix3d::Zero();
  plane.center = Eigen::Vector3d::Zero();
  plane.normal = Eigen::Vector3d::Zero();
  plane.points_size = points.size();
  plane.radius = 0;

  for (auto pi : points) {
    plane.cov += pi * pi.transpose();
    plane.center += pi;
  }
  plane.center = plane.center / plane.points_size;

  plane.cov =
      plane.cov / plane.points_size - plane.center * plane.center.transpose();

  Eigen::EigenSolver<Eigen::Matrix3d> es(plane.cov);
  Eigen::Matrix3cd evecs = es.eigenvectors();
  Eigen::Vector3cd evals = es.eigenvalues();

  Eigen::Vector3d evalsReal;
  evalsReal = evals.real();
  Eigen::Matrix3d::Index evalsMin, evalsMax;
  evalsReal.rowwise().sum().minCoeff(&evalsMin);
  evalsReal.rowwise().sum().maxCoeff(&evalsMax);
  int evalsMid = 3 - evalsMin - evalsMax;
  if (evalsReal(evalsMin) < config_setting_.plane_detection_thre_) {
    plane.normal << evecs.real()(0, evalsMin), evecs.real()(1, evalsMin),
        evecs.real()(2, evalsMin);

    if (plane.normal.dot(Eigen::Vector3d::UnitZ()) < 0) {
      plane.normal = -plane.normal;
    }
    plane.min_eigen_value = evalsReal(evalsMin);
    plane.radius = sqrt(evalsReal(evalsMax));
    plane.is_plane = true;

    plane.intercept = -(plane.normal(0) * plane.center(0) +
                        plane.normal(1) * plane.center(1) +
                        plane.normal(2) * plane.center(2));
  } else {
    plane.is_plane = false;
    plane.normal << evecs.real()(0, evalsMin), evecs.real()(1, evalsMin),
        evecs.real()(2, evalsMin);
    plane.min_eigen_value = evalsReal(evalsMin);
  }
  return plane;
}

cloud_t::Ptr adr_manager_t::voxel_to_plane_cloud(
    const std::vector<voxel_map_t::value_type> &voxels) const {
  cloud_t::Ptr cld(new cloud_t);
  cld->resize(voxels.size());
  std::transform(std::execution::par_unseq, voxels.begin(), voxels.end(),
                 cld->begin(),
                 [](const auto &pair) { return pair.second->plane; });
  return cld;
}

void adr_manager_t::build_connection(
    voxel_map_t &voxel_map,
    std::vector<voxel_map_t::value_type> &planes) const {
  std::for_each(planes.begin(), planes.end(),
                [&](const voxel_map_t::value_type &pair) {
                  auto voxels = pair.second;
                  for (int i = 0; i < SEARCH_DIRECTION_NUM; i++) {
                    if (voxels->is_check_connect[i]) {
                      continue;
                    }
                    voxel_loc_t neighbor = pair.first + SEARCH_DIRECTION[i];
                    auto near = voxel_map.find(neighbor);
                    if (near == voxel_map.end()) {
                      voxels->is_check_connect[i] = true;
                      voxels->connect[i] = false;
                    } else {
                      connect_neighbor(voxels, i, near->second);
                    }
                  }
                });
}

void adr_manager_t::connect_neighbor(voxel_t::ptr &voxel_a, size_t idx_a,
                                        voxel_t::ptr &voxel_b) const {
  size_t idx_b = ANTI_SEARCH_DIRECTION_ID[idx_a];
  voxel_a->is_check_connect[idx_a] = true;
  voxel_b->is_check_connect[idx_b] = true;

  if (!voxel_b->plane.is_plane) {
    voxel_a->connect[idx_a] = false;
    voxel_b->connect[idx_b] = true;
    voxel_b->connect_voxels[idx_b] = voxel_a;
  } else if (is_normal_close(voxel_a->plane.normal, voxel_b->plane.normal,
                             config_setting_.plane_merge_normal_thre_)) {
    voxel_a->connect[idx_a] = true;
    voxel_b->connect[idx_b] = true;
    voxel_a->connect_voxels[idx_a] = voxel_b;
    voxel_b->connect_voxels[idx_b] = voxel_a;
  } else {
    voxel_a->connect[idx_a] = false;
    voxel_b->connect[idx_b] = false;
  }
}

bool is_need_proj(const voxel_t *const &tree) {
  bool is_plane = tree->plane.is_plane;
  bool is_has_enough_points = tree->points.size() > 10;
  return !is_plane && is_has_enough_points;
}

bool is_connected_with_other_plane(const voxel_t::const_ptr voxel) {
  bool ret = false;
  for (int i = 0; i < SEARCH_DIRECTION_NUM; i++) {
    if (voxel->is_check_connect[i] && voxel->connect[i]) {
      ret = true;
      break;
    }
  }
  return ret;
}

bool adr_manager_t::is_projected_same_normal(
    const voxel_t::const_ptr voxel, const Eigen::Vector3d &normal) const {
  return std::any_of(voxel->proj_normal_vec.begin(),
                     voxel->proj_normal_vec.end(),
                     [&normal](const Eigen::Vector3d &n) {
                       return is_normal_close(n, normal, 0.5);
                     });
}

proj_info_t::ptr adr_manager_t::get_proj_info(
    voxel_map_t &voxel_map, const voxel_pair_t &pair) const {
  auto proj_info = std::make_shared<proj_info_t>();
  proj_info->projection_center = pair.second->plane.center;
  proj_info->projection_normal = pair.second->plane.normal;
  auto &proj_voxels = proj_info->proj_voxels;
  proj_voxels.reserve(27);
  for (auto &dir : search_27_t::instance()) {
    auto loc = pair.first + dir;

    if (voxel_map.find(loc) == voxel_map.end()) {
      continue;
    }

    auto voxel = voxel_map.at(loc);

    if (voxel->plane.is_plane) {
      continue;
    }

    if (is_projected_same_normal(voxel, proj_info->projection_normal)) {
      continue;
    }
    voxel->proj_normal_vec.push_back(proj_info->projection_normal);
    proj_voxels.push_back(voxel);
    proj_info->points_num += voxel->points.size();
  }
  return proj_info;
}

std::shared_ptr<std::vector<proj_info_t::ptr>>
adr_manager_t::extract_proj_points(voxel_map_t &voxel_map) const {
  std::shared_ptr<std::vector<proj_info_t::ptr>> proj_info_vec(
      new std::vector<proj_info_t::ptr>);
  proj_info_vec->reserve(voxel_map.size());
  for (auto &[loc, tree] : voxel_map) {
    if (tree->plane.is_plane) {
      continue;
    }

    if (tree->points.size() <= 10) {
      continue;
    }

    for (int i = 0; i < SEARCH_DIRECTION_NUM; i++) {
      if (!tree->connect[i]) {
        continue;
      }

      auto neighbor = tree->connect_voxels[i];
      if (!is_connected_with_other_plane(neighbor)) {
        continue;
      }
      proj_info_vec->push_back(get_proj_info(voxel_map, {loc, neighbor}));
    }
  }
  return proj_info_vec;
}

cloud_t::Ptr adr_manager_t::extract_img_features(
    voxel_map_t &voxel_map) {
  auto proj_info_vec = extract_proj_points(voxel_map);

  std::vector<cloud_t::Ptr> cld_vec(proj_info_vec->size());
  std::atomic<size_t> num{0};
  std::transform(std::execution::par_unseq, proj_info_vec->begin(),
                 proj_info_vec->end(), cld_vec.begin(),
                 [&](const proj_info_t::ptr &proj_info) {
                   const auto &&ret = do_project(proj_info);
                   num += ret->size();
                   return ret;
                 });

  cloud_t::Ptr cld(new cloud_t);
  cld->reserve(num);
  std::for_each(cld_vec.begin(), cld_vec.end(), [&cld](const cloud_t::Ptr &ps) {
    cld->insert(cld->end(), ps->begin(), ps->end());
  });

  cld = filter_by_intensity(cld);

  if (cld->size() > config_setting_.maximum_corner_num_) {
    std::sort(cld->points.begin(), cld->points.end(),
              [](const pcl::PointXYZINormal &a, const pcl::PointXYZINormal &b)
                  -> bool { return a.intensity > b.intensity; });
    cld->resize(config_setting_.maximum_corner_num_);
  }
  return cld;
}

Eigen::Vector4d plane_coeff(const Eigen::Vector3d &center,
                            const Eigen::Vector3d &normal) {
  return {normal[0], normal[1], normal[2], -center.dot(normal)};
}

Eigen::Matrix4d proj_matrix(const Eigen::Vector4d &plane_coeff) {
  auto &A = plane_coeff[0];
  auto &B = plane_coeff[1];
  auto &C = plane_coeff[2];
  auto &D = plane_coeff[3];
  const double sqr_norm = A * A + B * B + C * C;
  return (Eigen::Matrix4d() <<
    (B * B + C * C), -A * B, -A * C, -A * D,
    -A * B, (A * A + C * C), -B * C, -B * D,
    -A * C, -B * C, (A * A + B * B), -C * D,
    0, 0, 0, sqr_norm).finished() / sqr_norm;
}

std::pair<Eigen::Vector3d, Eigen::Vector3d> plane_axises(
    const Eigen::Vector4d &plane_coeff) {
  Eigen::Vector3d x_axis(1, 1, 0);
  if (plane_coeff[2] != 0) {
    x_axis[2] = -(plane_coeff[0] + plane_coeff[1]) / plane_coeff[2];
  } else if (plane_coeff[1] != 0) {
    x_axis[1] = -plane_coeff[0] / plane_coeff[1];
  } else {
    x_axis[0] = 0;
    x_axis[1] = 1;
  }
  x_axis.normalize();
  Eigen::Vector3d y_axis = plane_coeff.head<3>().cross(x_axis);
  y_axis.normalize();
  return {x_axis, y_axis};
}

void image_t::build_pixels(double res) {
  auto x_range =
      std::minmax_element(p2ds.begin(), p2ds.end(),
                          [](const Eigen::Vector2d &a,
                             const Eigen::Vector2d &b) { return a[0] < b[0]; });
  auto y_range =
      std::minmax_element(p2ds.begin(), p2ds.end(),
                          [](const Eigen::Vector2d &a,
                             const Eigen::Vector2d &b) { return a[1] < b[1]; });
  min_x = x_range.first->x();
  max_x = x_range.second->x();
  min_y = y_range.first->y();
  max_y = y_range.second->y();

  width = size_t((max_x - min_x) / res + pixel_block_size);
  height = size_t((max_y - min_y) / res + pixel_block_size);

  pixels.resize(width * height);
  for (auto iter = p2ds.begin(); iter != p2ds.end(); ++iter) {
    size_t x = (iter->x() - min_x) / res;
    size_t y = (iter->y() - min_y) / res;
    pixels[y * width + x].push_back(iter);
  }
}

image_t::ptr adr_manager_t::create_image(
    const proj_info_t::const_ptr &proj_info) const {
  auto img = std::make_shared<image_t>();
  img->center = proj_info->projection_center;
  img->normal = proj_info->projection_normal;
  img->plane_coeff = plane_coeff(img->center, img->normal);
  img->proj_matrix = proj_matrix(img->plane_coeff);
  auto [x_axis, y_axis] = plane_axises(img->plane_coeff);
  img->plane_x = plane_coeff(img->center, x_axis);
  img->plane_y = plane_coeff(img->center, y_axis);

  img->p3ds.reserve(proj_info->points_num);
  img->p2ds.reserve(proj_info->points_num);
  for (auto &voxel : proj_info->proj_voxels) {
    std::for_each(voxel->points.begin(), voxel->points.end(),
                  [&](const Eigen::Vector3d &p) {
                    Eigen::Vector4d p4(p[0], p[1], p[2], 1);
                    double dis = std::abs(p4.dot(img->plane_coeff));
                    if (dis >= config_setting_.proj_dis_min_ &&
                        dis <= config_setting_.proj_dis_max_) {
                      img->push_back(p4);
                    }
                  });
  }

  if (img->p3ds.size() <= 5) {
    return img;
  }

  img->build_pixels(config_setting_.proj_image_resolution_);

  return img;
}

std::pair<size_t, size_t> max_pixel_in_block(const image_t::ptr &img, int x,
                                             int y) {
  size_t max_sz = 0;
  size_t max_id = 0;
  for (int yy = y; yy < y + pixel_block_size; yy++) {
    for (int xx = x; xx < x + pixel_block_size; xx++) {
      auto idx = yy * img->width + xx;
      auto sz = img->pixels[idx].size();
      if (sz > max_sz) {
        max_sz = sz;
        max_id = idx;
      }
    }
  }
  return {max_sz, max_id};
}

std::shared_ptr<std::vector<size_t>> adr_manager_t::filter_pixel_block(
    const image_t::ptr &img) const {
  size_t w_b = img->width / pixel_block_size;
  size_t h_b = img->height / pixel_block_size;
  std::shared_ptr<std::vector<size_t>> pixel_idx(new std::vector<size_t>);
  pixel_idx->resize(w_b * h_b);

  size_t cnt = 0;
  for (int y = 0; y < h_b; y++) {
    for (int x = 0; x < w_b; x++) {
      auto [sz, id] =
          max_pixel_in_block(img, x * pixel_block_size, y * pixel_block_size);

      if (sz >= config_setting_.corner_thre_) {
        pixel_idx->at(cnt) = id;
        cnt++;
      }
    }
  }
  pixel_idx->resize(cnt);
  return pixel_idx;
}

cloud_t::Ptr adr_manager_t::do_project(
    const proj_info_t::const_ptr &proj_info) {
  auto img = create_image(proj_info);

  auto pixel_idx_vec = filter_pixel_block(img);

  cloud_t::Ptr features(new cloud_t(pixel_idx_vec->size(), 1));
  std::transform(pixel_idx_vec->begin(), pixel_idx_vec->end(),
                 features->begin(),
                 [&](const size_t &idx) { return img->reproject(idx); });

  return features;
}

bool is_bigger_point_exist_in_radius(
    const std::vector<int> &k_idx,
    const pcl::PointCloud<pcl::PointXYZINormal>::ConstPtr &cld) {
  const auto cur_intensity = cld->points[k_idx[0]].intensity;
  return k_idx.size() > 1 &&
         std::any_of(k_idx.begin() + 1, k_idx.end(),
                     [&](const int &idx) -> bool {
                       return cld->points[idx].intensity >= cur_intensity;
                     });
}

cloud_t::Ptr adr_manager_t::filter_by_intensity(
    const cloud_t::ConstPtr &cld) const {
  if (cld->empty()) return cloud_t::Ptr(new cloud_t);

  const auto radius = config_setting_.non_max_suppression_radius_;
  std::vector<bool> is_add_vec(cld->size(), true);
  pcl::KdTreeFLANN<pcl::PointXYZINormal> kd_tree;
  kd_tree.setInputCloud(cld);

  std::transform(cld->begin(), cld->end(), is_add_vec.begin(),
                 [&](const pcl::PointXYZINormal &p) {
                   std::vector<int> k_idx;
                   std::vector<float> k_dis;
                   kd_tree.radiusSearch(p, radius, k_idx, k_dis);
                   return !is_bigger_point_exist_in_radius(k_idx, cld);
                 });

  cloud_t::Ptr ret(new cloud_t);
  ret->reserve(cld->size());
  for (size_t i = 0; i < cld->size(); i++) {
    if (is_add_vec[i]) {
      ret->push_back(cld->points[i]);
    }
  }
  return ret;
}

trangle_t::vec_ptr adr_manager_t::create_trangels_from_one_point(
    const cloud_t::ConstPtr &cld, const std::vector<int> &k_idx) const {
  const auto min_dis_threshold = config_setting_.descriptor_min_len_;
  const auto max_dis_threshold = config_setting_.descriptor_max_len_;
  const auto sz = k_idx.size() - 1;
  const auto combine_num = sz * (sz - 1) / 2;
  const auto &p0 = cld->points[k_idx[0]];
  trangle_t::vec_ptr ret(new trangle_t::vec_t);
  ret->reserve(combine_num);
  for (size_t i = 1; i < k_idx.size() - 1; i++) {
    for (size_t j = i + 1; j < k_idx.size(); j++) {
      trangle_t tri(p0, cld->points[k_idx[i]], cld->points[k_idx[j]]);
      if (tri.sides[0] < min_dis_threshold ||
          tri.sides[2] > max_dis_threshold) {
        continue;
      }
      ret->push_back(tri);
    }
  }
  return ret;
}

desc_t::const_vec_ptr adr_manager_t::build_stdesc(
    const cloud_t::Ptr &cld) const {
  if (cld->empty()) return std::make_shared<desc_t::const_vec_t>();
  int search_num = config_setting_.descriptor_near_num_;
  pcl::KdTreeFLANN<point_t> kd_tree;
  kd_tree.setInputCloud(cld);
  std::vector<trangle_t::vec_ptr> tri_vecs(cld->size());
  std::atomic<size_t> tri_num{0};
  std::transform(std::execution::par_unseq, cld->begin(), cld->end(),
                 tri_vecs.begin(), [&](const pcl::PointXYZINormal &p) {
                   std::vector<int> k_idx;
                   std::vector<float> k_dis;
                   kd_tree.nearestKSearch(p, search_num, k_idx, k_dis);
                   auto ret = create_trangels_from_one_point(cld, k_idx);
                   tri_num += ret->size();
                   return ret;
                 });

  double scale = 1.0 / config_setting_.std_side_resolution_;
  std::unordered_set<voxel_loc_t> is_added;
  auto desc_vec = std::make_shared<desc_t::const_vec_t>();
  is_added.reserve(tri_num);
  desc_vec->reserve(tri_num);
  for (auto &vec : tri_vecs) {
    std::for_each(vec->begin(), vec->end(), [&](const trangle_t &tri) {
      auto &&loc = (tri.sides * 1e3).cast<int64_t>();
      auto [iter, is_success] = is_added.emplace(loc);
      if (is_success) {
        auto desc = std::make_shared<desc_t>(tri);
        desc->sides *= scale;
        desc->frame_id = current_frame_id_;
        desc_vec->push_back(desc);
      }
    });
  }

  return desc_vec;
};

desc_t::const_vec_ptr adr_manager_t::filter_match_desc(
    desc_t::const_ptr cur_desc, const desc_t::const_vec_ptr descs) const {
  double dis_threshold =
      cur_desc->sides.norm() * config_setting_.rough_dis_threshold_;
  auto ret = std::make_shared<desc_t::const_vec_t>();
  ret->reserve(descs->size());
  std::for_each(
      descs->begin(), descs->end(), [&](const desc_t::const_ptr &desc) {
        if (cur_desc->frame_id - desc->frame_id <=
            config_setting_.skip_near_num_) {
          return;
        }

        if ((cur_desc->sides - desc->sides).norm() >= dis_threshold) {
          return;
        }

        double intensity_diff =
            2.0 *
            (cur_desc->vertex_intencities - desc->vertex_intencities).norm() /
            (cur_desc->vertex_intencities + desc->vertex_intencities).norm();
        if (intensity_diff >= config_setting_.vertex_diff_threshold_) {
          return;
        }

        ret->push_back(desc);
      });

  return ret;
}

adr_manager_t::prv_descs_vec_ptr adr_manager_t::find_near_descs(
    const desc_t::const_ptr &desc) const {
  std::shared_ptr<std::vector<desc_t::const_vec_ptr>> ret(
      new std::vector<desc_t::const_vec_ptr>);
  ret->reserve(27);
  for (auto dir : search_27_t::instance()) {
    stdesc_loc_t position;
    position.x = (int)(desc->sides[0] + dir[0]);
    position.y = (int)(desc->sides[1] + dir[1]);
    position.z = (int)(desc->sides[2] + dir[2]);
    auto iter = data_base_.find(position);
    if (iter == data_base_.end()) {
      continue;
    }

    Eigen::Vector3d voxel_center((double)position.x + 0.5,
                                 (double)position.y + 0.5,
                                 (double)position.z + 0.5);
    if ((desc->sides - voxel_center).norm() >= 1.5) {
      continue;
    }

    ret->push_back(filter_match_desc(desc, iter->second));
  }
  return ret;
}

std::shared_ptr<std::vector<match_frame_t>> adr_manager_t::build_match_frame(
    const desc_t::const_vec_ptr stds_vec) const {
  std::vector<prv_descs_vec_ptr> match_descs_vec(stds_vec->size());
  std::transform(stds_vec->begin(), stds_vec->end(),
                 match_descs_vec.begin(), [&](const desc_t::const_ptr &desc) {
                   return find_near_descs(desc);
                 });

  std::vector<match_list_t> match_map(current_frame_id_ - 1);
  for (size_t i = 0; i < stds_vec->size(); i++) {
    auto cur_desc = stds_vec->at(i);
    for (auto match_descs : *match_descs_vec[i]) {
      for (auto match_desc : *match_descs) {
        match_map[match_desc->frame_id].emplace_back(stds_vec->at(i),
                                                     match_desc);
      }
    }
  }

  std::vector<frameid_sz_t> sort_helper(match_map.size());
  for (size_t i = 0; i < match_map.size(); i++) {
    sort_helper[i] = {i, match_map[i].size()};
  }
  std::sort(sort_helper.begin(), sort_helper.end(), frameid_sz_t::greater);

  auto start = sort_helper.begin();
  auto stop =
      sort_helper.begin() +
      std::min((size_t)config_setting_.candidate_num_, sort_helper.size());
  std::shared_ptr<std::vector<match_frame_t>> ret(
      new std::vector<match_frame_t>(std::distance(start, stop)));
  std::transform(start, stop, ret->begin(), [&](const frameid_sz_t &p) {
    match_frame_t match_triangle_list;
    match_triangle_list.match_id.first = current_frame_id_;
    match_triangle_list.match_id.second = p.frame_id;
    match_triangle_list.match_list.swap(match_map[p.frame_id]);
    return match_triangle_list;
  });
  return ret;
}

Eigen::Affine3d adr_manager_t::one_step_ICP(const match_pair_t &pair) const {
  Eigen::Affine3d ret = Eigen::Affine3d::Identity();
  Eigen::Matrix3d src = Eigen::Matrix3d::Zero();
  Eigen::Matrix3d ref = Eigen::Matrix3d::Zero();
  src.col(0) = pair.first->vertex_a - pair.first->center;
  src.col(1) = pair.first->vertex_b - pair.first->center;
  src.col(2) = pair.first->vertex_c - pair.first->center;
  ref.col(0) = pair.second->vertex_a - pair.second->center;
  ref.col(1) = pair.second->vertex_b - pair.second->center;
  ref.col(2) = pair.second->vertex_c - pair.second->center;
  Eigen::Matrix3d covariance = src * ref.transpose();
  Eigen::JacobiSVD<Eigen::MatrixXd> svd(
      covariance, Eigen::ComputeThinU | Eigen::ComputeThinV);
  Eigen::Matrix3d V = svd.matrixV();
  Eigen::Matrix3d U = svd.matrixU();

  Eigen::Matrix3d rot = V * U.transpose();
  if (rot.determinant() < 0) {
    Eigen::Matrix3d K;
    K << 1, 0, 0, 0, 1, 0, 0, 0, -1;
    rot = V * K * U.transpose();
  }
  ret.translation() = -rot * pair.first->center + pair.second->center;
  ret.linear() = rot;
  return ret;
}

std::shared_ptr<match_list_t> adr_manager_t::filter_match_pairs_about_trans(
    const Eigen::Affine3d &transformation, const match_list_t &pairs) const {
  const double dis_threshold = config_setting_.vtx_dis_threshold_;
  auto matches = std::make_shared<match_list_t>();
  matches->reserve(pairs.size());
  std::for_each(pairs.begin(), pairs.end(), [&](const match_pair_t &pair) {
    auto A = transformation * pair.first->vertex_a;
    auto B = transformation * pair.first->vertex_b;
    auto C = transformation * pair.first->vertex_c;
    bool is_A_ok = (A - pair.second->vertex_a).norm() < dis_threshold;
    bool is_B_ok = (B - pair.second->vertex_b).norm() < dis_threshold;
    bool is_C_ok = (C - pair.second->vertex_c).norm() < dis_threshold;
    if (is_A_ok && is_B_ok && is_C_ok) {
      matches->push_back(pair);
    }
  });
  return matches;
}

match_info_t adr_manager_t::find_best_transform(
    const match_frame_t &candidate_matcher) const {
  if (candidate_matcher.match_list.size() == 0) {
    return {};
  }

  int skip_len = (int)(candidate_matcher.match_list.size() / 50) + 1;
  int use_size = candidate_matcher.match_list.size() / skip_len;

  std::vector<size_t> idxes(use_size);
  std::iota(idxes.begin(), idxes.end(), 0);

  std::vector<match_info_t> match_info_vec(use_size);
  std::transform(
      idxes.begin(), idxes.end(), match_info_vec.begin(), [&](const size_t &i) {
        match_info_t ret;
        ret.trans = one_step_ICP(candidate_matcher.match_list[i * skip_len]);
        ret.matches = filter_match_pairs_about_trans(
            ret.trans, candidate_matcher.match_list);
        return ret;
      });

  auto best_info_iter =
      std::max_element(match_info_vec.begin(), match_info_vec.end(),
                       [](const match_info_t &a, const match_info_t &b) {
                         return a.matches->size() < b.matches->size();
                       });

  return std::move(*best_info_iter);
}

bool adr_manager_t::is_plane_close(const Eigen::Vector3d &center_a,
                                      const Eigen::Vector3d &normal_a,
                                      const Eigen::Vector3d &center_b,
                                      const Eigen::Vector3d &normal_b) const {
  bool is_normal_close_ok =
      is_normal_close(normal_a, normal_b, config_setting_.normal_threshold_);
  bool is_point_close_ok =
      abs(normal_b.dot(center_a - center_b)) < config_setting_.dis_threshold_;
  return is_normal_close_ok && is_point_close_ok;
}

double adr_manager_t::evalute_transform(const cloud_t::Ptr &src,
                                           const cloud_t::Ptr &tgt,
                                           const Eigen::Affine3d &trans) {
  static const int K = 3;
  pcl::KdTreeFLANN<pcl::PointXYZINormal> tree(false);
  tree.setInputCloud(tgt);
  std::atomic<size_t> cnt{0};

  std::for_each(
      std::execution::par_unseq, src->begin(), src->end(),
      [&](const point_t &p) {
        Eigen::Vector3d pi = trans * p.getVector3fMap().cast<double>();
        pcl::PointXYZINormal sp;
        sp.x = pi[0];
        sp.y = pi[1];
        sp.z = pi[2];

        std::vector<int> k_idx(K);
        std::vector<float> k_dis(K);
        if (tree.nearestKSearch(sp, K, k_idx, k_dis) == 0) {
          return;
        }

        Eigen::Vector3d ni =
            trans.linear() * p.getNormalVector3fMap().cast<double>();
        cnt += std::any_of(k_idx.begin(), k_idx.end(), [&](const int &idx) {
          auto &p = tgt->at(idx);
          Eigen::Vector3d tpi = p.getVector3fMap().cast<double>();
          Eigen::Vector3d tni = p.getNormalVector3fMap().cast<double>();
          return is_plane_close(pi, ni, tpi, tni);
        });
      });
  return double(cnt) / src->size();
}

void adr_manager_t::PlaneGeomrtricIcp(
    const pcl::PointCloud<pcl::PointXYZINormal>::Ptr &source_cloud,
    const pcl::PointCloud<pcl::PointXYZINormal>::Ptr &target_cloud,
    std::pair<Eigen::Vector3d, Eigen::Matrix3d> &transform) {
  pcl::KdTreeFLANN<pcl::PointXYZ>::Ptr kd_tree(
      new pcl::KdTreeFLANN<pcl::PointXYZ>);
  pcl::PointCloud<pcl::PointXYZ>::Ptr input_cloud(
      new pcl::PointCloud<pcl::PointXYZ>);
  for (size_t i = 0; i < target_cloud->size(); i++) {
    pcl::PointXYZ pi;
    pi.x = target_cloud->points[i].x;
    pi.y = target_cloud->points[i].y;
    pi.z = target_cloud->points[i].z;
    input_cloud->push_back(pi);
  }
  kd_tree->setInputCloud(input_cloud);

  ceres::Manifold *quaternion_manifold = new ceres::EigenQuaternionManifold;
  ceres::Problem problem;
  ceres::LossFunction *loss_function = nullptr;
  Eigen::Matrix3d rot = transform.second;
  Eigen::Quaterniond q(rot);
  Eigen::Vector3d t = transform.first;
  double para_q[4] = {q.x(), q.y(), q.z(), q.w()};
  double para_t[3] = {t(0), t(1), t(2)};
  problem.AddParameterBlock(para_q, 4, quaternion_manifold);
  problem.AddParameterBlock(para_t, 3);
  Eigen::Map<Eigen::Quaterniond> q_last_curr(para_q);
  Eigen::Map<Eigen::Vector3d> t_last_curr(para_t);
  std::vector<int> pointIdxNKNSearch(1);
  std::vector<float> pointNKNSquaredDistance(1);
  int useful_match = 0;

  for (size_t i = 0; i < source_cloud->size(); i++) {
    pcl::PointXYZINormal searchPoint = source_cloud->points[i];
    Eigen::Vector3d pi(searchPoint.x, searchPoint.y, searchPoint.z);
    pi = rot * pi + t;
    pcl::PointXYZ use_search_point;
    use_search_point.x = pi[0];
    use_search_point.y = pi[1];
    use_search_point.z = pi[2];
    Eigen::Vector3d ni(searchPoint.normal_x, searchPoint.normal_y,
                       searchPoint.normal_z);
    ni = rot * ni;
    if (kd_tree->nearestKSearch(use_search_point, 1, pointIdxNKNSearch,
                                pointNKNSquaredDistance) > 0) {
      pcl::PointXYZINormal nearstPoint =
          target_cloud->points[pointIdxNKNSearch[0]];
      Eigen::Vector3d tpi(nearstPoint.x, nearstPoint.y, nearstPoint.z);
      Eigen::Vector3d tni(nearstPoint.normal_x, nearstPoint.normal_y,
                          nearstPoint.normal_z);
      Eigen::Vector3d normal_inc = ni - tni;
      Eigen::Vector3d normal_add = ni + tni;
      double point_to_point_dis = (pi - tpi).norm();
      double point_to_plane = fabs(tni.transpose() * (pi - tpi));

      if ((normal_inc.norm() < config_setting_.normal_threshold_ ||
           normal_add.norm() < config_setting_.normal_threshold_) &&
          point_to_plane < config_setting_.dis_threshold_ &&
          point_to_point_dis < 3) {
        useful_match++;
        ceres::CostFunction *cost_function;
        Eigen::Vector3d curr_point(source_cloud->points[i].x,
                                   source_cloud->points[i].y,
                                   source_cloud->points[i].z);
        Eigen::Vector3d curr_normal(source_cloud->points[i].normal_x,
                                    source_cloud->points[i].normal_y,
                                    source_cloud->points[i].normal_z);

        cost_function =
            plaen_ceres_func_t::Create(curr_point, curr_normal, tpi, tni);
        problem.AddResidualBlock(cost_function, loss_function, para_q, para_t);
      }
    }
  }
  ceres::Solver::Options options;
  options.linear_solver_type = ceres::SPARSE_NORMAL_CHOLESKY;
  options.max_num_iterations = 100;
  options.minimizer_progress_to_stdout = false;
  ceres::Solver::Summary summary;
  ceres::Solve(options, &problem, &summary);
  Eigen::Quaterniond q_opt(para_q[3], para_q[0], para_q[1], para_q[2]);
  rot = q_opt.toRotationMatrix();
  t << t_last_curr(0), t_last_curr(1), t_last_curr(2);
  transform.first = t;
  transform.second = rot;
}
