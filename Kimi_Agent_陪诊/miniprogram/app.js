const api = require('./utils/api')

App({
  globalData: {
    userInfo: null,
    openid: '',
    city: '',
    province: '',
  },

  onLaunch() {
    this.login()
    this.detectCity()
  },

  // WeChat login → get openid
  login() {
    wx.login({
      success: (res) => {
        if (res.code) {
          // Send code to backend to exchange for openid
          // For dev: use a mock openid
          this.globalData.openid = 'wx_' + Date.now()
          wx.setStorageSync('openid', this.globalData.openid)
        }
      }
    })
  },

  // Auto-detect city
  detectCity() {
    // Try GPS first
    wx.getLocation({
      type: 'gcj02',
      success: (res) => {
        api.detectCity(res.latitude, res.longitude).then(data => {
          this.globalData.city = data.city
          this.globalData.province = data.province
          wx.setStorageSync('city', data.city)
        }).catch(() => {
          this.fallbackCityDetect()
        })
      },
      fail: () => {
        this.fallbackCityDetect()
      }
    })
  },

  fallbackCityDetect() {
    api.detectCity().then(data => {
      this.globalData.city = data.city
      this.globalData.province = data.province
      wx.setStorageSync('city', data.city)
    }).catch(() => {
      this.globalData.city = '北京市'
      wx.setStorageSync('city', '北京市')
    })
  }
})
