import axios from "axios";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const http = axios.create({ baseURL: API, timeout: 30000 });

export const api = {
  getStats: () => http.get("/stats"),
  getPlatforms: () => http.get("/platforms"),

  listProjects: (params) => http.get("/projects", { params }),
  getProject: (id) => http.get(`/projects/${id}`),
  createProject: (data) => http.post("/projects", data),
  updateProject: (id, data) => http.put(`/projects/${id}`, data),
  deleteProject: (id) => http.delete(`/projects/${id}`),
  validateProject: (id) => http.post(`/projects/${id}/validate`),
  generateConfig: (id) => http.post(`/projects/${id}/generate`),
  getRevisions: (id) => http.get(`/projects/${id}/revisions`),
  exportProject: (id, format) => http.get(`/projects/${id}/export/${format}`),
  importProject: (payload) => http.post("/projects/import", payload),
  createFromTemplate: (id) => http.post(`/projects/from-template/${id}`),

  listTemplates: (params) => http.get("/templates", { params }),
  getTemplate: (id) => http.get(`/templates/${id}`),
  createTemplate: (data) => http.post("/templates", data),
  updateTemplate: (id, data) => http.put(`/templates/${id}`, data),
  deleteTemplate: (id) => http.delete(`/templates/${id}`),
  duplicateTemplate: (id) => http.post(`/templates/${id}/duplicate`),
  toggleTemplateLock: (id) => http.post(`/templates/${id}/lock`),
};
