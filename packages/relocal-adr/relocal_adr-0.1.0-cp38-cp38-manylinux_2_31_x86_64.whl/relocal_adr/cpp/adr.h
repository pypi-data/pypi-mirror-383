#pragma once

#include <ceres/ceres.h>
#include <ceres/rotation.h>
#include <pcl/common/io.h>
#include <pcl/kdtree/kdtree_flann.h>
#include <stdio.h>

#include <Eigen/Core>
#include <Eigen/Dense>
#include <Eigen/StdVector>
#include <fstream>
#include <mutex>
#include <sstream>
#include <string>
#include <unordered_map>
#include <deque>

#define HASH_P 116101
#define MAX_N 10000000000
#define MAX_FRAME_N 20000

static const int pixel_block_size = 5;

using voxel_loc_t = Eigen::Matrix<int64_t, 3, 1>;
template <>
struct std::hash<voxel_loc_t> {
  int64_t operator()(const voxel_loc_t &s) const {
    return (((s[2] * HASH_P) % MAX_N + s[1]) * HASH_P) % MAX_N + s[0];
  }
};

static const int SEARCH_DIRECTION_NUM = 6;

static const std::array<voxel_loc_t, 6> SEARCH_DIRECTION = {
    voxel_loc_t(1, 0, 0),  voxel_loc_t(0, 1, 0),  voxel_loc_t(0, 0, 1),
    voxel_loc_t(-1, 0, 0), voxel_loc_t(0, -1, 0), voxel_loc_t(0, 0, -1)};

static const std::array<int, 6> ANTI_SEARCH_DIRECTION_ID = {3, 4, 5, 0, 1, 2};

class search_27_t : public std::array<voxel_loc_t, 27> {
 public:
  static const search_27_t &instance() {
    static search_27_t instance_;
    return instance_;
  }

  static constexpr size_t size() { return 27; }

 private:
  search_27_t() {
    int id = 0;
    for (int i = -1; i < 2; i++) {
      for (int j = -1; j < 2; j++) {
        for (int k = -1; k < 2; k++) {
          this->at(id) = voxel_loc_t(i, j, k);
          id++;
        }
      }
    }
  }

  ~search_27_t() {}
  search_27_t(const search_27_t &) = delete;
  search_27_t &operator=(const search_27_t &) = delete;
};

struct ConfigSetting {
  int stop_skip_enable_ = 0;
  double ds_size_ = 0.5;
  int maximum_corner_num_ = 30;

  double plane_merge_normal_thre_;
  double plane_merge_dis_thre_;
  double plane_detection_thre_ = 0.01;
  double voxel_size_ = 1.0;
  int voxel_init_num_ = 10;
  double proj_image_resolution_ = 0.5;
  double proj_dis_min_ = 0.2;
  double proj_dis_max_ = 5;
  double corner_thre_ = 10;

  int descriptor_near_num_ = 10;
  double descriptor_min_len_ = 1;
  double descriptor_max_len_ = 10;
  double non_max_suppression_radius_ = 3.0;
  double std_side_resolution_ = 0.2;
  double vtx_dis_threshold_ = 3.0;

  int skip_near_num_ = 50;
  int candidate_num_ = 50;
  int sub_frame_num_ = 10;
  double rough_dis_threshold_ = 0.03;
  double vertex_diff_threshold_ = 0.7;
  double icp_threshold_ = 0.5;
  double normal_threshold_ = 0.1;
  double dis_threshold_ = 0.3;
};

using point_t = pcl::PointXYZINormal;
using cloud_t = pcl::PointCloud<point_t>;

void down_sampling_voxel(pcl::PointCloud<pcl::PointXYZI> &pl_feat,
                         double voxel_size);

void down_sample(pcl::PointCloud<pcl::PointXYZI>::Ptr pl_feat,
                 double voxel_size);

struct plaen_ceres_func_t {
  plaen_ceres_func_t(Eigen::Vector3d curr_point_, Eigen::Vector3d curr_normal_,
                     Eigen::Vector3d target_point_,
                     Eigen::Vector3d target_normal_)
      : curr_point(curr_point_),
        curr_normal(curr_normal_),
        target_point(target_point_),
        target_normal(target_normal_) {};
  template <typename T>
  bool operator()(const T *q, const T *t, T *residual) const {
    Eigen::Quaternion<T> q_w_curr{q[3], q[0], q[1], q[2]};
    Eigen::Matrix<T, 3, 1> t_w_curr{t[0], t[1], t[2]};
    Eigen::Matrix<T, 3, 1> cp{T(curr_point.x()), T(curr_point.y()),
                              T(curr_point.z())};
    Eigen::Matrix<T, 3, 1> point_w;
    point_w = q_w_curr * cp + t_w_curr;
    Eigen::Matrix<T, 3, 1> point_target(
        T(target_point.x()), T(target_point.y()), T(target_point.z()));
    Eigen::Matrix<T, 3, 1> norm(T(target_normal.x()), T(target_normal.y()),
                                T(target_normal.z()));
    residual[0] = norm.dot(point_w - point_target);
    return true;
  }

  static ceres::CostFunction *Create(const Eigen::Vector3d curr_point_,
                                     const Eigen::Vector3d curr_normal_,
                                     Eigen::Vector3d target_point_,
                                     Eigen::Vector3d target_normal_) {
    return (new ceres::AutoDiffCostFunction<plaen_ceres_func_t, 1, 4, 3>(
        new plaen_ceres_func_t(curr_point_, curr_normal_, target_point_,
                               target_normal_)));
  }

  Eigen::Vector3d curr_point;
  Eigen::Vector3d curr_normal;
  Eigen::Vector3d target_point;
  Eigen::Vector3d target_normal;
};

struct plane_t {
  Eigen::Vector3d center;
  Eigen::Vector3d normal;
  Eigen::Matrix3d cov;
  float radius = 0;
  float min_eigen_value = 1;
  float intercept = 0;
  int points_size = 0;
  bool is_plane = false;
  uint64_t id = 0;

  operator pcl::PointXYZINormal() const {
    pcl::PointXYZINormal p;
    p.x = center[0];
    p.y = center[1];
    p.z = center[2];
    p.normal_x = normal[0];
    p.normal_y = normal[1];
    p.normal_z = normal[2];
    p.intensity = min_eigen_value;
    return p;
  }
};

struct voxel_t {
  using ptr = std::shared_ptr<voxel_t>;
  using const_ptr = std::shared_ptr<const voxel_t>;

  std::vector<Eigen::Vector3d> points;

  plane_t plane;

  std::vector<Eigen::Vector3d> proj_normal_vec;

  std::array<bool, SEARCH_DIRECTION_NUM> is_check_connect{false};

  std::array<bool, SEARCH_DIRECTION_NUM> connect{false};

  std::array<voxel_t::ptr, SEARCH_DIRECTION_NUM> connect_voxels{nullptr};

  u_int64_t idx = 0;
};

using voxel_map_t = std::unordered_map<voxel_loc_t, voxel_t::ptr>;
using voxel_pair_t = std::pair<voxel_loc_t, voxel_t::ptr>;

struct proj_info_t {
  using ptr = std::shared_ptr<proj_info_t>;
  using const_ptr = std::shared_ptr<const proj_info_t>;
  Eigen::Vector3d projection_normal;
  Eigen::Vector3d projection_center;
  std::vector<voxel_t::const_ptr> proj_voxels;
  size_t points_num = 0;
};

struct pixel_t {
  using iter = std::vector<pixel_t>::iterator;
  using p2d_iter = std::vector<Eigen::Vector2d>::const_iterator;

  std::vector<p2d_iter> iters;

  double sum_x = 0.;

  double sum_y = 0.;

  void push_back(const p2d_iter &iter) {
    iters.push_back(iter);
    sum_x += iter->x();
    sum_y += iter->y();
  }

  size_t size() const { return iters.size(); }

  double x() const { return sum_x / (double)iters.size(); }

  double y() const { return sum_y / (double)iters.size(); }
};

struct image_t {
  using ptr = std::shared_ptr<image_t>;
  using const_ptr = std::shared_ptr<const image_t>;

  std::vector<Eigen::Vector3d> p3ds;

  std::vector<Eigen::Vector2d> p2ds;

  std::vector<pixel_t> pixels;

  Eigen::Vector4d plane_coeff;

  Eigen::Vector4d plane_x;

  Eigen::Vector4d plane_y;

  Eigen::Matrix4d proj_matrix;

  Eigen::Vector3d center;

  Eigen::Vector3d normal;

  size_t width, height;

  double max_x, min_x;

  double max_y, min_y;

  pcl::PointXYZINormal reproject(size_t pixel_idx) const {
    const auto &pixel = pixels[pixel_idx];
    const auto &&x = pixel.x();
    const auto &&y = pixel.y();
    auto coord = center + x * plane_x.head<3>() + y * plane_y.head<3>();
    pcl::PointXYZINormal pi;
    pi.x = coord[0];
    pi.y = coord[1];
    pi.z = coord[2];
    pi.intensity = pixel.size();
    pi.normal_x = normal[0];
    pi.normal_y = normal[1];
    pi.normal_z = normal[2];
    return pi;
  }

  void push_back(const Eigen::Vector4d &p) {
    Eigen::Vector4d cur_project = proj_matrix * p;
    double project_x = cur_project.dot(plane_x);
    double project_y = cur_project.dot(plane_y);
    p2ds.emplace_back(project_x, project_y);
    p3ds.emplace_back(p[0], p[1], p[2]);
  }

  void build_pixels(double resolution);
};

struct desc_t {
  using ptr = std::shared_ptr<desc_t>;
  using vec_t = std::vector<ptr>;
  using vec_ptr = std::shared_ptr<vec_t>;
  using const_ptr = std::shared_ptr<const desc_t>;
  using const_vec_t = std::vector<const_ptr>;
  using const_vec_ptr = std::shared_ptr<const const_vec_t>;

  Eigen::Vector3d sides;

  Eigen::Vector3d angles;

  Eigen::Vector3d center;

  unsigned int frame_id;

  Eigen::Vector3d vertex_a;

  Eigen::Vector3d vertex_b;

  Eigen::Vector3d vertex_c;

  Eigen::Vector3d vertex_intencities;

  Eigen::Vector3d normals[3];

  Eigen::Vector3d normal() const {
    Eigen::Vector3d normal = (vertex_b - vertex_a).cross(vertex_c - vertex_a);
    normal.normalize();
    if (normal.dot(Eigen::Vector3d::UnitZ()) < 0) {
      normal = -normal;
    }
    return normal;
  }
};

class trangle_t {
 public:
  using vec_t = std::vector<trangle_t>;
  using vec_ptr = std::shared_ptr<vec_t>;

  trangle_t(const pcl::PointXYZINormal &p1, const pcl::PointXYZINormal &p2,
            const pcl::PointXYZINormal &p3)
      : vert{p1, p2, p3} {
    normalization();
  }

  trangle_t(const std::array<pcl::PointXYZINormal, 3> &ps) : vert(ps) {
    normalization();
  }

  operator desc_t() const {
    desc_t desc;
    desc.vertex_a = vert[0].getVector3fMap().cast<double>();
    desc.vertex_b = vert[1].getVector3fMap().cast<double>();
    desc.vertex_c = vert[2].getVector3fMap().cast<double>();
    desc.normals[0] = vert[0].getNormalVector3fMap().cast<double>();
    desc.normals[1] = vert[1].getNormalVector3fMap().cast<double>();
    desc.normals[2] = vert[2].getNormalVector3fMap().cast<double>();
    desc.center = (desc.vertex_a + desc.vertex_b + desc.vertex_c) / 3;
    desc.vertex_intencities << vert[0].intensity, vert[1].intensity,
        vert[2].intensity;
    desc.sides = sides;
    Eigen::Vector3d normal_1 = vert[0].getNormalVector3fMap().cast<double>();
    Eigen::Vector3d normal_2 = vert[1].getNormalVector3fMap().cast<double>();
    Eigen::Vector3d normal_3 = vert[2].getNormalVector3fMap().cast<double>();
    desc.angles[0] = fabs(5 * normal_1.dot(normal_2));
    desc.angles[1] = fabs(5 * normal_1.dot(normal_3));
    desc.angles[2] = fabs(5 * normal_3.dot(normal_2));
    return desc;
  }

  double distance(const pcl::PointXYZINormal &a,
                  const pcl::PointXYZINormal &b) {
    return sqrt(pow(a.x - b.x, 2) + pow(a.y - b.y, 2) + pow(a.z - b.z, 2));
  }

  void normalization() {
    std::array<std::pair<double, int>, 3> sort_helper{
        std::make_pair(distance(vert[0], vert[1]), 2),
        std::make_pair(distance(vert[0], vert[2]), 1),
        std::make_pair(distance(vert[1], vert[2]), 0)};
    std::sort(sort_helper.begin(), sort_helper.end(),
              [](auto &a, auto &b) { return a.first < b.first; });
    auto tmp_vert = vert;
    std::transform(sort_helper.begin(), sort_helper.end(), vert.begin(),
                   [&](auto &a) { return tmp_vert[a.second]; });
    sides << sort_helper[0].first, sort_helper[1].first, sort_helper[2].first;
  }

  std::array<pcl::PointXYZINormal, 3> vert;
  Eigen::Vector3d sides;
};

struct stdesc_loc_t {
  int64_t x, y, z, a, b, c;

  stdesc_loc_t(int64_t vx = 0, int64_t vy = 0, int64_t vz = 0, int64_t va = 0,
               int64_t vb = 0, int64_t vc = 0)
      : x(vx), y(vy), z(vz), a(va), b(vb), c(vc) {}

  bool operator==(const stdesc_loc_t &other) const {
    return (x == other.x && y == other.y && z == other.z);
  }
};

template <>
struct std::hash<stdesc_loc_t> {
  int64_t operator()(const stdesc_loc_t &s) const {
    int64_t x = s.x << 42;
    int64_t y = s.y << 21;
    int64_t z = s.z;
    return x | y | z;
  }
};

using match_pair_t = std::pair<desc_t::const_ptr, desc_t::const_ptr>;
using match_list_t = std::vector<match_pair_t>;

struct match_frame_t {
  using ptr = std::shared_ptr<match_frame_t>;
  using const_ptr = std::shared_ptr<const match_frame_t>;
  match_list_t match_list;
  std::pair<int, int> match_id;
};

struct match_info_t {
  Eigen::Affine3d trans = Eigen::Affine3d::Identity();
  std::shared_ptr<match_list_t> matches;

  size_t size() const { return matches ? matches->size() : 0; }
};

struct frameid_sz_t {
  size_t frame_id = 0;
  size_t sz = 0;

  bool operator>(const frameid_sz_t &other) const {
    if (sz != other.sz) {
      return sz > other.sz;
    } else {
      return frame_id < other.frame_id;
    }
  }

  static bool greater(const frameid_sz_t &a, const frameid_sz_t &b) {
    return a > b;
  }
};

struct PenaltyInfo {
  size_t key_frame_id = 0;
  size_t loop_frame_id = 0;
  double penalty_matches = 0;
  double key_flatness = 0;
  double loop_flatness = 0;
  double penalty_alpha = 0;
  double penalty_flatness = 0;
  double penalty = 0;

  std::string to_string() const {
    std::ostringstream oss;
    oss << key_frame_id << "," << loop_frame_id << "," << penalty_matches << ","
        << key_flatness << "," << loop_flatness << "," << penalty_alpha << ","
        << penalty_flatness << "," << penalty;
    return oss.str();
  }
};


class adr_manager_t {
 public:
  adr_manager_t() = default;

  unsigned int current_frame_id_;

  adr_manager_t(ConfigSetting &config_setting)
      : config_setting_(config_setting) {
    current_frame_id_ = 0;
  };
  
  std::vector<pcl::PointCloud<pcl::PointXYZI>::Ptr> key_cloud_vec_;

  std::vector<pcl::PointCloud<pcl::PointXYZINormal>::Ptr> corner_cloud_vec_;

  std::vector<pcl::PointCloud<pcl::PointXYZINormal>::Ptr> plane_cloud_vec_;


  desc_t::const_vec_ptr GenerateSTDescs(
      pcl::PointCloud<pcl::PointXYZI>::Ptr &input_cloud);

  void SearchLoop(desc_t::const_vec_ptr stds_vec,
                  std::pair<int, double> &loop_result,
                  std::pair<Eigen::Vector3d, Eigen::Matrix3d> &loop_transform,
                  match_list_t &loop_std_pair);

  void AddSTDescs(const desc_t::const_vec_ptr stds_vec);

  void PlaneGeomrtricIcp(
      const pcl::PointCloud<pcl::PointXYZINormal>::Ptr &source_cloud,
      const pcl::PointCloud<pcl::PointXYZINormal>::Ptr &target_cloud,
      std::pair<Eigen::Vector3d, Eigen::Matrix3d> &transform);

 private:
  ConfigSetting config_setting_;
  std::unordered_map<stdesc_loc_t, std::shared_ptr<desc_t::const_vec_t>>
      data_base_;


  void to_voxel_map(const pcl::PointCloud<pcl::PointXYZI>::Ptr &input_cloud,
                    voxel_map_t &voxel_map) const;

  void extract_plane_voxel(voxel_map_t &voxel_map,
                           std::vector<voxel_map_t::value_type> &planes) const;

  plane_t extract_plane_from_points(
      const std::vector<Eigen::Vector3d> &points) const;

  cloud_t::Ptr voxel_to_plane_cloud(
      const std::vector<voxel_map_t::value_type> &voxels) const;

  void build_connection(voxel_map_t &voxel_map,
                        std::vector<voxel_map_t::value_type> &planes) const;

  void connect_neighbor(voxel_t::ptr &voxel_a, size_t idx_a,
                        voxel_t::ptr &voxel_b) const;

  bool is_projected_same_normal(const voxel_t::const_ptr voxel,
                                const Eigen::Vector3d &normal) const;

  proj_info_t::ptr get_proj_info(voxel_map_t &map,
                                 const voxel_pair_t &pair) const;

  std::shared_ptr<std::vector<proj_info_t::ptr>> extract_proj_points(
      voxel_map_t &voxel_map) const;

  cloud_t::Ptr extract_img_features(voxel_map_t &voxel_map);

  image_t::ptr create_image(const proj_info_t::const_ptr &proj_info) const;

  std::shared_ptr<std::vector<size_t>> filter_pixel_block(
      const image_t::ptr &image) const;

  cloud_t::Ptr do_project(const proj_info_t::const_ptr &proj_info);

  cloud_t::Ptr filter_by_intensity(const cloud_t::ConstPtr &cld) const;

  trangle_t::vec_ptr create_trangels_from_one_point(
      const cloud_t::ConstPtr &cld, const std::vector<int> &k_idx) const;

  desc_t::const_vec_ptr build_stdesc(const cloud_t::Ptr &corner_points) const;

  desc_t::const_vec_ptr filter_match_desc(
      desc_t::const_ptr cur_desc, const desc_t::const_vec_ptr descs) const;

  using prv_descs_vec_ptr =
      std::shared_ptr<std::vector<desc_t::const_vec_ptr>>;

  prv_descs_vec_ptr find_near_descs(const desc_t::const_ptr &desc) const;

  std::shared_ptr<std::vector<match_frame_t>> build_match_frame(
      const desc_t::const_vec_ptr stds_vec) const;

  Eigen::Affine3d one_step_ICP(const match_pair_t &pair) const;

  std::shared_ptr<match_list_t> filter_match_pairs_about_trans(
      const Eigen::Affine3d &transformation, const match_list_t &pairs) const;

  match_info_t find_best_transform(
      const match_frame_t &candidate_matcher) const;

  bool is_plane_close(const Eigen::Vector3d &center_a,
                      const Eigen::Vector3d &normal_a,
                      const Eigen::Vector3d &center_b,
                      const Eigen::Vector3d &normal_b) const;

  double evalute_transform(const cloud_t::Ptr &src, const cloud_t::Ptr &tgt,
                           const Eigen::Affine3d &trans);
};