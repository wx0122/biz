Component({
  properties: {
    escort: {
      type: Object,
      value: {}
    }
  },
  methods: {
    onTap() {
      this.triggerEvent('tap', { escort: this.data.escort })
    }
  }
})
