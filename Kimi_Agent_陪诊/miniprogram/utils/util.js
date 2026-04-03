// Format date to YYYY-MM-DD
function formatDate(date) {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

// Get next N days for date picker
function getNextDays(n) {
  const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
  const days = []
  for (let i = 0; i < n; i++) {
    const d = new Date()
    d.setDate(d.getDate() + i)
    days.push({
      value: formatDate(d),
      label: i === 0 ? '今天' : i === 1 ? '明天' : `${d.getMonth() + 1}/${d.getDate()}`,
      weekday: weekdays[d.getDay()]
    })
  }
  return days
}

// Mask phone number: 138****8888
function maskPhone(phone) {
  if (!phone || phone.length < 7) return phone || ''
  return phone.slice(0, 3) + '****' + phone.slice(-4)
}

// Status text mapping
const statusText = {
  pending: '待支付',
  paid: '待服务',
  confirmed: '已确认',
  completed: '已完成',
  cancelled: '已取消',
  processing: '培训中',
}

function getStatusText(status) {
  return statusText[status] || status
}

module.exports = {
  formatDate,
  getNextDays,
  maskPhone,
  getStatusText,
}
