package com.gtd.core.filter;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

@Component
public class LoggingFilter extends OncePerRequestFilter {

    private static final DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
            throws ServletException, IOException {

        // Thực thi request tiếp theo trong chuỗi
        try {
            filterChain.doFilter(request, response);
        } finally {
            // Lấy các thông tin cần thiết
            String time = LocalDateTime.now().format(formatter);
            String ip = getClientIp(request);
            String method = request.getMethod();
            String endpoint = request.getRequestURI();
            
            // Lấy thêm query string nếu có để log đầy đủ URI
            String queryString = request.getQueryString();
            if (queryString != null) {
                endpoint = endpoint + "?" + queryString;
            }
            
            int statusCode = response.getStatus();

            // Format đúng yêu cầu: [Thời gian] - [IP Khách] - [Method] [Endpoint] - [Status Code]
            String logMessage = String.format("[%s] - [%s] - [%s] [%s] - [%d]",
                    time, ip, method, endpoint, statusCode);

            // In thẳng ra System.out để Cloud có thể gom log dễ dàng
            System.out.println(logMessage);
        }
    }

    private String getClientIp(HttpServletRequest request) {
        String remoteAddr = request.getHeader("X-Forwarded-For");
        if (remoteAddr == null || remoteAddr.isEmpty()) {
            remoteAddr = request.getRemoteAddr();
        } else {
            remoteAddr = remoteAddr.split(",")[0].trim();
        }
        return remoteAddr;
    }
}
