Component({
  properties: {
    hospital: {
      type: Object,
      value: {}
    }
  },
  methods: {
    onTap() {
      this.triggerEvent('tap', { hospital: this.data.hospital })
    }
  }
})
