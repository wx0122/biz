const api = require('../../utils/api')

Page({
  data: {
    userInfo: {},
    stats: {
      totalOrders: 0,
      bookings: 0,
      trainings: 0,
      pendingOrders: 0
    },
    records: [],
    showRecordsModal: false,
    showEditModal: false,
    editForm: {
      nickname: '',
      phone: ''
    }
  },

  onLoad() {
    this.loadProfile()
    this.loadStats()
  },

  onShow() {
    this.loadStats()
  },

  onPullDownRefresh() {
    Promise.all([this.loadProfile(), this.loadStats()])
      .then(() => wx.stopPullDownRefresh())
  },

  async loadProfile() {
    try {
      const res = await api.getUserProfile()
      const userInfo = res.data || res || {}
      this.setData({ userInfo })
    } catch (e) {
      // User might not exist yet
      const openid = wx.getStorageSync('openid')
      if (openid) {
        this.setData({ userInfo: { openid } })
      }
    }
  },

  async loadStats() {
    try {
      const res = await api.getOrders()
      const orders = res.data || res || []
      const bookings = orders.filter(o => o.type === 'booking')
      const trainings = orders.filter(o => o.type === 'training')
      const pending = orders.filter(o => o.status === 'pending')
      this.setData({
        stats: {
          totalOrders: orders.length,
          bookings: bookings.length,
          trainings: trainings.length,
          pendingOrders: pending.length
        }
      })
    } catch (e) {
      console.error('Failed to load stats:', e)
    }
  },

  editProfile() {
    this.setData({
      showEditModal: true,
      editForm: {
        nickname: this.data.userInfo.nickname || '',
        phone: this.data.userInfo.phone || ''
      }
    })
  },

  onEditNickname(e) { this.setData({ 'editForm.nickname': e.detail.value }) },
  onEditPhone(e) { this.setData({ 'editForm.phone': e.detail.value }) },

  async saveProfile() {
    const { nickname, phone } = this.data.editForm
    if (phone && !/^1\d{10}$/.test(phone)) {
      wx.showToast({ title: '请输入正确的手机号', icon: 'none' })
      return
    }
    try {
      await api.updateUserProfile({ nickname, phone })
      wx.showToast({ title: '保存成功', icon: 'success' })
      this.setData({ showEditModal: false })
      this.loadProfile()
    } catch (e) {
      wx.showToast({ title: '保存失败', icon: 'none' })
    }
  },

  closeEdit() {
    this.setData({ showEditModal: false })
  },

  async viewRecords() {
    try {
      const res = await api.getUserRecords()
      this.setData({
        records: res.data || res || [],
        showRecordsModal: true
      })
    } catch (e) {
      wx.showToast({ title: '加载失败', icon: 'none' })
    }
  },

  closeRecords() {
    this.setData({ showRecordsModal: false })
  },

  goToOrders(e) {
    wx.switchTab({ url: '/pages/orders/orders' })
  },

  goTraining() {
    wx.navigateTo({ url: '/pages/training/training' })
  },

  goBooking() {
    wx.navigateTo({ url: '/pages/booking/booking' })
  },

  showAbout() {
    wx.showModal({
      title: '关于我们',
      content: '专业陪诊服务平台，为您提供贴心的医院陪诊、代办服务。让就医更简单、更安心。',
      showCancel: false
    })
  },

  contactService() {
    wx.makePhoneCall({
      phoneNumber: '400-000-0000',
      fail: () => {}
    })
  }
})
