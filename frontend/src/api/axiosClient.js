import axios from 'axios';
import { toast } from 'react-toastify';

const axiosClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add a response interceptor
axiosClient.interceptors.response.use(
  function (response) {
    // API Contract: { status: "success" | "error", data: { ... }, message: "..." }
    const resData = response.data;
    
    // Nếu status trả về là error từ phía Backend (200 OK nhưng logic là error)
    if (resData && resData.status === 'error') {
      toast.error(resData.message || 'Đã có lỗi xảy ra từ máy chủ!');
      return Promise.reject(new Error(resData.message || 'Lỗi từ Backend'));
    }
    
    // Trả về trực tiếp phần data để Component dễ sử dụng
    return resData;
  },
  function (error) {
    // Xử lý các lỗi HTTP (400, 401, 403, 404, 500, Network Error, v.v.)
    const errorMessage = error.response?.data?.message || error.message || 'Lỗi kết nối mạng hoặc máy chủ!';
    toast.error(errorMessage);
    return Promise.reject(error);
  }
);

export default axiosClient;
