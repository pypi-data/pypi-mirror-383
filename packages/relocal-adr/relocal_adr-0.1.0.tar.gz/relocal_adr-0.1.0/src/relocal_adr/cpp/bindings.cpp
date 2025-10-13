#ifndef PROJ_NAME
#error "PROJ_NAME macro must be defined"
#endif

#include "adr.h"
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include <memory>

namespace py = pybind11;

struct Feature {
    std::shared_ptr<desc_t> ptr;
    explicit Feature(const std::shared_ptr<desc_t>& p) : ptr(p) {}
    std::vector<double> sides()   const { return {ptr->sides[0],   ptr->sides[1],   ptr->sides[2]}; }
    std::vector<double> angles()  const { return {ptr->angles[0],  ptr->angles[1],  ptr->angles[2]}; }
    std::vector<double> center()  const { return {ptr->center[0],  ptr->center[1],  ptr->center[2]}; }
    unsigned int frame_id()       const { return ptr->frame_id; }
};

class ADR {
public:
    std::unique_ptr<adr_manager_t> impl;

    explicit ADR(const py::dict& d) {
        ConfigSetting cfg;
        if (d.contains("ds_size"))                    cfg.ds_size_                    = py::float_(d["ds_size"]);
        if (d.contains("maximum_corner_num"))         cfg.maximum_corner_num_         = py::int_(d["maximum_corner_num"]);
        if (d.contains("plane_merge_normal_thre"))    cfg.plane_merge_normal_thre_    = py::float_(d["plane_merge_normal_thre"]);
        if (d.contains("plane_merge_dis_thre"))       cfg.plane_merge_dis_thre_       = py::float_(d["plane_merge_dis_thre"]);
        if (d.contains("plane_detection_thre"))       cfg.plane_detection_thre_       = py::float_(d["plane_detection_thre"]);
        if (d.contains("voxel_size"))                 cfg.voxel_size_                 = py::float_(d["voxel_size"]);
        if (d.contains("voxel_init_num"))             cfg.voxel_init_num_             = py::int_(d["voxel_init_num"]);
        if (d.contains("proj_image_resolution"))      cfg.proj_image_resolution_      = py::float_(d["proj_image_resolution"]);
        if (d.contains("proj_dis_min"))               cfg.proj_dis_min_               = py::float_(d["proj_dis_min"]);
        if (d.contains("proj_dis_max"))               cfg.proj_dis_max_               = py::float_(d["proj_dis_max"]);
        if (d.contains("corner_thre"))                cfg.corner_thre_                = py::float_(d["corner_thre"]);
        if (d.contains("descriptor_near_num"))        cfg.descriptor_near_num_        = py::int_(d["descriptor_near_num"]);
        if (d.contains("descriptor_min_len"))         cfg.descriptor_min_len_         = py::float_(d["descriptor_min_len"]);
        if (d.contains("descriptor_max_len"))         cfg.descriptor_max_len_         = py::float_(d["descriptor_max_len"]);
        if (d.contains("non_max_suppression_radius")) cfg.non_max_suppression_radius_ = py::float_(d["non_max_suppression_radius"]);
        if (d.contains("std_side_resolution"))        cfg.std_side_resolution_        = py::float_(d["std_side_resolution"]);
        if (d.contains("vtx_dis_threshold"))          cfg.vtx_dis_threshold_          = py::float_(d["vtx_dis_threshold"]);
        if (d.contains("skip_near_num"))              cfg.skip_near_num_              = py::int_(d["skip_near_num"]);
        if (d.contains("candidate_num"))              cfg.candidate_num_              = py::int_(d["candidate_num"]);
        if (d.contains("sub_frame_num"))              cfg.sub_frame_num_              = py::int_(d["sub_frame_num"]);
        if (d.contains("rough_dis_threshold"))        cfg.rough_dis_threshold_        = py::float_(d["rough_dis_threshold"]);
        if (d.contains("vertex_diff_threshold"))      cfg.vertex_diff_threshold_      = py::float_(d["vertex_diff_threshold"]);
        if (d.contains("icp_threshold"))              cfg.icp_threshold_              = py::float_(d["icp_threshold"]);
        if (d.contains("normal_threshold"))           cfg.normal_threshold_           = py::float_(d["normal_threshold"]);
        if (d.contains("dis_threshold"))              cfg.dis_threshold_              = py::float_(d["dis_threshold"]);

        impl = std::make_unique<adr_manager_t>(cfg);
    }

    std::vector<Feature> extract(py::array_t<float, py::array::c_style | py::array::forcecast> points) {
        auto buf = points.request();
        if (buf.ndim != 2 || buf.shape[1] != 3)
            throw std::runtime_error("Input must be Nx3 float32 array");
        size_t N = buf.shape[0];
        auto cloud = pcl::PointCloud<pcl::PointXYZI>::Ptr(new pcl::PointCloud<pcl::PointXYZI>());
        cloud->resize(N);
        const float* data = static_cast<const float*>(buf.ptr);
        for (size_t i = 0; i < N; ++i) {
            (*cloud)[i].x = data[i * 3 + 0];
            (*cloud)[i].y = data[i * 3 + 1];
            (*cloud)[i].z = data[i * 3 + 2];
            (*cloud)[i].intensity = 1.0f;
        }
        auto descs = impl->GenerateSTDescs(cloud);
        std::vector<Feature> feats;
        feats.reserve(descs->size());
        for (auto& d : *descs) feats.emplace_back(std::const_pointer_cast<desc_t>(d));
        return feats;
    }

    std::tuple<int, float> query(const std::vector<Feature>& features) {
        auto descs = std::make_shared<desc_t::const_vec_t>();
        for (const auto& f : features) descs->push_back(f.ptr);
        std::pair<int, double> loop_result;
        std::pair<Eigen::Vector3d, Eigen::Matrix3d> loop_transform;
        match_list_t loop_std_pair;
        impl->SearchLoop(descs, loop_result, loop_transform, loop_std_pair);
        return std::make_tuple(loop_result.first, static_cast<float>(loop_result.second));
    }

    void update(const std::vector<Feature>& features) {
        auto descs = std::make_shared<desc_t::const_vec_t>();
        for (const auto& f : features) descs->push_back(f.ptr);
        impl->AddSTDescs(descs);
    }
};

PYBIND11_MODULE(PROJ_NAME, m, py::mod_gil_not_used()) {
    py::class_<Feature>(m, "Feature")
        .def_property_readonly("sides",   &Feature::sides)
        .def_property_readonly("angles",  &Feature::angles)
        .def_property_readonly("center",  &Feature::center)
        .def_property_readonly("frame_id",&Feature::frame_id);

    py::class_<ADR>(m, "ADR")
        .def(py::init<const py::dict&>(), py::arg("params"))
        .def("extract", &ADR::extract, py::arg("points"))
        .def("query",   &ADR::query,   py::arg("features"))
        .def("update",  &ADR::update,  py::arg("features"));
}
