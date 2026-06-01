import cubeStatsMock from '../mocks/cubeStatsMock.json';
// import axiosClient from '../api/axiosClient';

const dashboardService = {
  getCubeStats: async (params) => {
    // REAL API:
    // return axiosClient.get(`/cube-stats?${params.toString()}`);
    
    // MOCK DATA IMPLEMENTATION:
    return new Promise((resolve) => {
      setTimeout(() => {
        // Giả lập việc axiosClient tự động bóc tách `resData.data` hoặc trả thẳng
        // Vì trong axiosClient ta return `resData`, nên ta mock y như những gì axiosClient trả ra
        // resData ở backend Java là: { status, data, message }
        resolve(cubeStatsMock); 
      }, 1500);
    });
  }
};

export default dashboardService;
