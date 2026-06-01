import axiosClient from '../api/axiosClient';

const predictionService = {
  predictRisk: async (payload) => {
    // REAL API:
    return axiosClient.post('/predictions', payload);
  }
};

export default predictionService;
