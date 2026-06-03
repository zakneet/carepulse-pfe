const hostname = window.location.hostname;
const apiBaseUrl =
  hostname === 'localhost' || hostname === '127.0.0.1'
    ? 'http://localhost:5000'
    : `http://${hostname}:5000`;

export const environment = {
  production: true,
  apiUrl: apiBaseUrl,
  weatherUrl: apiBaseUrl
};
