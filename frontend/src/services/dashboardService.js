import axiosClient from '../api/axiosClient';

const dashboardService = {
  getCubeStats: async (params) => {
    // REAL API:
    return axiosClient.get(`/cube-stats?${params.toString()}`);
  }
};

export default dashboardService;
