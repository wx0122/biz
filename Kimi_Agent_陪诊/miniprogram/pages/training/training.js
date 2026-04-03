const api = require('../../utils/api')

Page({
  data: {
    courses: [],
    selectedCourseId: null,
    selectedCourse: null,
    loading: true,
    submitting: false,
    showPayModal: false,
    showSuccessModal: false,
    formData: {
      name: '',
      phone: '',
      id_number: '',
      remark: ''
    }
  },

  onLoad() {
    this.loadCourses()
  },

  onPullDownRefresh() {
    this.loadCourses().then(() => wx.stopPullDownRefresh())
  },

  async loadCourses() {
    this.setData({ loading: true })
    try {
      const res = await api.getCourses()
      this.setData({ courses: res.data || res || [] })
    } catch (e) {
      console.error('Failed to load courses:', e)
      wx.showToast({ title: '加载失败', icon: 'none' })
    } finally {
      this.setData({ loading: false })
    }
  },

  selectCourse(e) {
    const id = e.currentTarget.dataset.id
    const course = this.data.courses.find(c => c.id == id)
    if (this.data.selectedCourseId === id) {
      this.setData({ selectedCourseId: null, selectedCourse: null })
    } else {
      this.setData({ selectedCourseId: id, selectedCourse: course })
    }
  },

  onInputName(e) { this.setData({ 'formData.name': e.detail.value }) },
  onInputPhone(e) { this.setData({ 'formData.phone': e.detail.value }) },
  onInputIdNumber(e) { this.setData({ 'formData.id_number': e.detail.value }) },
  onInputRemark(e) { this.setData({ 'formData.remark': e.detail.value }) },

  submitRegistration() {
    const { name, phone } = this.data.formData
    if (!name.trim()) {
      wx.showToast({ title: '请输入姓名', icon: 'none' })
      return
    }
    if (!/^1\d{10}$/.test(phone)) {
      wx.showToast({ title: '请输入正确的手机号', icon: 'none' })
      return
    }
    if (!this.data.selectedCourseId) {
      wx.showToast({ title: '请选择课程', icon: 'none' })
      return
    }
    this.setData({ showPayModal: true })
  },

  closePayModal() {
    this.setData({ showPayModal: false })
  },

  async payWithWechat() {
    await this.doRegister('wechat')
  },

  async payWithAlipay() {
    await this.doRegister('alipay')
  },

  async doRegister(payMethod) {
    this.setData({ submitting: true, showPayModal: false })
    try {
      const openid = wx.getStorageSync('openid') || 'guest'
      const data = {
        openid,
        course_id: this.data.selectedCourseId,
        name: this.data.formData.name,
        phone: this.data.formData.phone,
        id_number: this.data.formData.id_number,
        remark: this.data.formData.remark
      }
      await api.registerTraining(data)

      // Create payment
      try {
        await api.createPayment({
          openid,
          type: 'training',
          reference_id: this.data.selectedCourseId,
          amount: this.data.selectedCourse.price,
          method: payMethod
        })
      } catch (payErr) {
        console.log('Payment mock:', payErr)
      }

      this.setData({ showSuccessModal: true })
    } catch (e) {
      console.error('Registration failed:', e)
      wx.showToast({ title: '报名失败，请重试', icon: 'none' })
    } finally {
      this.setData({ submitting: false })
    }
  },

  goToOrders() {
    this.setData({ showSuccessModal: false })
    wx.switchTab({ url: '/pages/orders/orders' })
  },

  resetForm() {
    this.setData({
      showSuccessModal: false,
      selectedCourseId: null,
      selectedCourse: null,
      formData: { name: '', phone: '', id_number: '', remark: '' }
    })
  }
})
