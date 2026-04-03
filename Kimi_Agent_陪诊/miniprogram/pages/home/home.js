const api = require('../../utils/api')
const app = getApp()

Page({
  data: {
    city: '',
    banners: [
      { id: 1, image: '/images/banner1.jpg' },
      { id: 2, image: '/images/banner2.jpg' },
      { id: 3, image: '/images/banner3.jpg' },
    ],
    hospitals: [],
    escorts: [],
    showCityPicker: false,
    allCities: [],
    hotCities: [],
    filteredCities: [],
    citySearchKey: '',
  },

  onShow() {
    const city = wx.getStorageSync('city') || app.globalData.city || ''
    this.setData({ city })
    this.loadData(city)
  },

  loadData(city) {
    api.getHospitals(city).then(res => {
      this.setData({ hospitals: res.items || [] })
    }).catch(() => {})

    api.getEscorts(city).then(res => {
      this.setData({ escorts: res.items || [] })
    }).catch(() => {})
  },

  // City picker
  onCityTap() {
    api.getCities().then(res => {
      this.setData({
        showCityPicker: true,
        allCities: res.items || [],
        hotCities: res.hot || [],
        filteredCities: res.items || [],
        citySearchKey: '',
      })
    }).catch(() => {
      this.setData({ showCityPicker: true })
    })
  },

  closeCityPicker() {
    this.setData({ showCityPicker: false })
  },

  selectCity(e) {
    const city = e.currentTarget.dataset.city
    wx.setStorageSync('city', city)
    app.globalData.city = city
    this.setData({ city, showCityPicker: false })
    this.loadData(city)
  },

  onCitySearch(e) {
    const key = e.detail.value
    const filtered = key
      ? this.data.allCities.filter(c => c.name.includes(key) || c.province.includes(key))
      : this.data.allCities
    this.setData({ citySearchKey: key, filteredCities: filtered })
  },

  goBooking() {
    wx.navigateTo({ url: '/pages/booking/booking' })
  },

  goTraining() {
    wx.navigateTo({ url: '/pages/training/training' })
  },
})
