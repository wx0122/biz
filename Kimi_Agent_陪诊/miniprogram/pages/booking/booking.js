const api = require('../../utils/api')
const util = require('../../utils/util')

Page({
  data: {
    step: 1,
    // Step 1
    hospitals: [],
    filteredHospitals: [],
    searchKey: '',
    selectedHospital: '',
    selectedHospitalName: '',
    // Step 2
    serviceTypes: [],
    selectedService: '2',
    selectedServiceName: '全程陪诊',
    dates: [],
    selectedDate: '',
    selectedTime: '',
    timeSlots: [
      { period: '上午', times: ['08:00', '09:00', '10:00', '11:00'] },
      { period: '下午', times: ['14:00', '15:00', '16:00', '17:00'] },
    ],
    // Step 3
    patientName: '',
    patientAge: '',
    phone: '',
    description: '',
    totalPrice: 268,
    submitting: false,
    // Modals
    showPayModal: false,
    showSuccess: false,
    lastOrderId: null,
  },

  onLoad() {
    const city = wx.getStorageSync('city') || ''
    api.getHospitals(city).then(res => {
      this.setData({
        hospitals: res.items || [],
        filteredHospitals: res.items || [],
      })
    }).catch(() => {})

    api.getServiceTypes().then(types => {
      this.setData({ serviceTypes: types })
    })

    this.setData({ dates: util.getNextDays(7) })
  },

  // Step 1
  onSearch(e) {
    const key = e.detail.value
    const filtered = key
      ? this.data.hospitals.filter(h => h.name.includes(key) || (h.address || '').includes(key))
      : this.data.hospitals
    this.setData({ searchKey: key, filteredHospitals: filtered })
  },

  selectHospital(e) {
    const id = e.currentTarget.dataset.id
    const h = this.data.hospitals.find(x => x.id === id)
    this.setData({ selectedHospital: id, selectedHospitalName: h ? h.name : '' })
  },

  // Step 2
  selectService(e) {
    const id = e.currentTarget.dataset.id
    const s = this.data.serviceTypes.find(x => x.id === id)
    this.setData({ selectedService: id, selectedServiceName: s ? s.name : '', totalPrice: s ? s.price : 0 })
  },

  selectDate(e) {
    this.setData({ selectedDate: e.currentTarget.dataset.value })
  },

  selectTime(e) {
    this.setData({ selectedTime: e.currentTarget.dataset.time })
  },

  // Step 3
  onInputName(e) { this.setData({ patientName: e.detail.value }) },
  onInputAge(e) { this.setData({ patientAge: e.detail.value }) },
  onInputPhone(e) { this.setData({ phone: e.detail.value }) },
  onInputDesc(e) { this.setData({ description: e.detail.value }) },

  nextStep() {
    this.setData({ step: this.data.step + 1 })
  },

  // Navigation back
  onBack() {
    if (this.data.step > 1) {
      this.setData({ step: this.data.step - 1 })
    } else {
      wx.navigateBack()
    }
  },

  // Submit
  submitBooking() {
    this.setData({ submitting: true })
    api.createBooking({
      hospital_id: parseInt(this.data.selectedHospital),
      service_type_id: parseInt(this.data.selectedService),
      date: this.data.selectedDate,
      time: this.data.selectedTime,
      patient_name: this.data.patientName,
      patient_age: this.data.patientAge,
      phone: this.data.phone,
      description: this.data.description,
    }).then(res => {
      this.setData({
        submitting: false,
        lastOrderId: res.booking ? res.booking.id : null,
        showPayModal: true,
      })
    }).catch(() => {
      this.setData({ submitting: false, showSuccess: true })
    })
  },

  // Payment
  closePayModal() {
    this.setData({ showPayModal: false })
  },

  payWechat() {
    this._pay('wechat')
  },

  payAlipay() {
    this._pay('alipay')
  },

  _pay(method) {
    if (!this.data.lastOrderId) {
      this.setData({ showPayModal: false, showSuccess: true })
      return
    }
    api.createPayment({
      order_type: 'booking',
      order_id: this.data.lastOrderId,
      method: method,
    }).then(res => {
      if (method === 'wechat' && res.pay_url && !res.pay_url.startsWith('mock://')) {
        // Real WeChat Pay: call wx.requestPayment with the params
        // wx.requestPayment({ ...JSON.parse(res.pay_url), success/fail })
      }
      // Mock mode or alipay: show success
      this.setData({ showPayModal: false, showSuccess: true })
    }).catch(() => {
      this.setData({ showPayModal: false, showSuccess: true })
    })
  },

  onSuccessConfirm() {
    wx.navigateBack()
  },
})
