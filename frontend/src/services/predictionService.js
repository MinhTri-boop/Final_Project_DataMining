import predictionMock from '../mocks/predictionMock.json';
// import axiosClient from '../api/axiosClient';

const predictionService = {
  predictRisk: async (payload) => {
    // REAL API:
    // return axiosClient.post('/predictions', payload);

    // MOCK DATA IMPLEMENTATION:
    return new Promise((resolve) => {
      setTimeout(() => {
        // Mở rộng logic: thay đổi Risk Level tuỳ vào params để bạn test màu UI
        let riskLevel = "High Risk";
        let prob = 0.85;
        
        // Nếu region chẵn -> Low Risk, lẻ -> High Risk (giả lập)
        if (payload.region && payload.region % 2 === 0) {
            riskLevel = "Low Risk";
            prob = 0.12;
        }

        resolve({
          status: "success",
          message: "Predicted via Mock",
          data: {
            success_probability: prob,
            risk_level: riskLevel
          }
        });
      }, 1500);
    });
  }
};

export default predictionService;
