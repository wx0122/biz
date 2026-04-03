// Backend API base URL — change to your server address in production
const BASE_URL = 'http://localhost:5050/api'

function getOpenid() {
  return wx.getStorageSync('openid') || 'guest'
}

function request(path, options = {}) {
  return new Promise((resolve, reject) => {
    wx.request({
      url: `${BASE_URL}${path}`,
      method: options.method || 'GET',
      data: options.data || {},
      header: {
        'Content-Type': 'application/json',
        'X-Openid': getOpenid(),
        ...(options.header || {})
      },
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data)
        } else {
          reject(res.data)
        }
      },
      fail: (err) => {
        reject(err)
      }
    })
  })
}

// ── Hospitals ────────────────────────────────────
function getHospitals(city, search) {
  let qs = ''
  if (city) qs += `city=${city}&`
  if (search) qs += `search=${search}&`
  return request(`/hospitals?${qs}`)
}

function getHospital(id) {
  return request(`/hospitals/${id}`)
}

// ── Escorts ──────────────────────────────────────
function getEscorts(city) {
  const qs = city ? `?city=${city}` : ''
  return request(`/escorts${qs}`)
}

// ── Service Types ────────────────────────────────
// (hardcoded since they rarely change)
function getServiceTypes() {
  return Promise.resolve([
    { id: '1', name: '普通陪诊', description: '基础陪同服务，包含挂号、排队、取报告', price: 128, features: ['陪同就诊', '协助沟通', '取药指引'] },
    { id: '2', name: '全程陪诊', description: '挂号+就诊+取药全流程', price: 268, features: ['代挂号', '全程陪同', '代取药', '报告代取'] },
    { id: '3', name: '特殊陪诊', description: '老人/儿童/孕妇专属', price: 368, features: ['专属陪护', '优先服务', '轮椅协助', '全程照顾'] },
  ])
}

// ── Bookings ─────────────────────────────────────
function createBooking(data) {
  return request('/bookings', { method: 'POST', data })
}

function getBookings() {
  return request('/bookings')
}

function cancelBooking(id) {
  return request(`/bookings/${id}/cancel`, { method: 'POST' })
}

// ── Training ─────────────────────────────────────
function getCourses() {
  return request('/training/courses')
}

function registerTraining(data) {
  return request('/training/register', { method: 'POST', data })
}

function getTrainingRegistrations() {
  return request('/training/registrations')
}

// ── Orders ───────────────────────────────────────
function getOrders(type) {
  const qs = type && type !== 'all' ? `?type=${type}` : ''
  return request(`/orders${qs}`)
}

// ── Users ────────────────────────────────────────
function getUserProfile() {
  return request('/users/me')
}

function updateUserProfile(data) {
  return request('/users/me', { method: 'PUT', data })
}

function getUserRecords() {
  return request('/users/records')
}

// ── Payments ─────────────────────────────────────
function createPayment(data) {
  return request('/payments/create', { method: 'POST', data })
}

function checkPaymentStatus(paymentNo) {
  return request(`/payments/status/${paymentNo}`)
}

// ── Cities ───────────────────────────────────────
function getCities() {
  return request('/cities')
}

function detectCity(lat, lng) {
  const qs = (lat && lng) ? `?lat=${lat}&lng=${lng}` : ''
  return request(`/cities/detect${qs}`)
}

function searchCities(q) {
  return request(`/cities/search?q=${q}`)
}

module.exports = {
  BASE_URL,
  getHospitals,
  getHospital,
  getEscorts,
  getServiceTypes,
  createBooking,
  getBookings,
  cancelBooking,
  getCourses,
  registerTraining,
  getTrainingRegistrations,
  getOrders,
  getUserProfile,
  updateUserProfile,
  getUserRecords,
  createPayment,
  checkPaymentStatus,
  getCities,
  detectCity,
  searchCities,
}
