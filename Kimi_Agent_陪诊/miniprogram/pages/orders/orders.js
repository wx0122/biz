const api = require('../../utils/api')

Page({
  data: {
    currentTab: 'all',
    orders: [],
    loading: true,
    statusText: {
      pending: '待支付',
      paid: '已支付',
      confirmed: '已确认',
      processing: '进行中',
      completed: '已完成',
      cancelled: '已取消'
    }
  },

  onLoad() {
    this.loadOrders()
  },

  onShow() {
    this.loadOrders()
  },

  onPullDownRefresh() {
    this.loadOrders().then(() => wx.stopPullDownRefresh())
  },

  async loadOrders() {
    this.setData({ loading: true })
    try {
      const res = await api.getOrders(this.data.currentTab)
      const orders = res.data || res || []
      this.setData({ orders })
    } catch (e) {
      console.error('Failed to load orders:', e)
      wx.showToast({ title: '加载失败', icon: 'none' })
    } finally {
      this.setData({ loading: false })
    }
  },

  switchTab(e) {
    const tab = e.currentTarget.dataset.tab
    if (tab !== this.data.currentTab) {
      this.setData({ currentTab: tab })
      this.loadOrders()
    }
  },

  viewOrder(e) {
    const item = e.currentTarget.dataset.item
    if (item.type === 'booking' && item.id) {
      wx.navigateTo({ url: `/pages/booking/booking?booking_id=${item.id}` })
    }
  },

  async cancelOrder(e) {
    const item = e.currentTarget.dataset.item
    const res = await new Promise(resolve => {
      wx.showModal({
        title: '确认取消',
        content: '确定要取消这个订单吗？',
        success: resolve
      })
    })
    if (!res.confirm) return

    try {
      if (item.type === 'booking') {
        await api.cancelBooking(item.id)
      }
      wx.showToast({ title: '已取消', icon: 'success' })
      this.loadOrders()
    } catch (e) {
      wx.showToast({ title: '取消失败', icon: 'none' })
    }
  },

  payOrder(e) {
    const item = e.currentTarget.dataset.item
    wx.showActionSheet({
      itemList: ['微信支付', '支付宝支付'],
      success: async (res) => {
        const method = res.tapIndex === 0 ? 'wechat' : 'alipay'
        try {
          const openid = wx.getStorageSync('openid') || 'guest'
          await api.createPayment({
            openid,
            type: item.type,
            reference_id: item.id,
            amount: item.amount || item.price,
            method
          })
          wx.showToast({ title: '支付成功', icon: 'success' })
          this.loadOrders()
        } catch (e) {
          wx.showToast({ title: '支付失败', icon: 'none' })
        }
      }
    })
  },

  goHome() {
    wx.switchTab({ url: '/pages/home/home' })
  }
})
