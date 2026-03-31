import { defineStore } from 'pinia'
import { apiGet, apiPut, getSocketIoUrl } from '@/utils/api'
import { io } from 'socket.io-client'

export const useSystemStore = defineStore('system', {
    state: () => ({
        powerMode: 'normal',
        lastUpdated: null,
        isInitialized: false,
        socket: null,
        psDisableAi: true,
        psDisableUploads: true,
        psDisableGcode: true
    }),

    actions: {
        async init() {
            if (this.isInitialized) return

            try {
                const res = await apiGet('/system/config')
                if (res.power_mode) {
                    this.powerMode = res.power_mode
                    this.lastUpdated = res.last_updated
                    this.psDisableAi = res.ps_disable_ai ?? true
                    this.psDisableUploads = res.ps_disable_uploads ?? true
                    this.psDisableGcode = res.ps_disable_gcode ?? true
                }
            } catch (err) {
                console.error("Failed to fetch system config", err)
            }

            // Listen to socket push events for real-time toggle
            if (!this.socket) {
                const token = localStorage.getItem('token')
                this.socket = io(getSocketIoUrl(), { auth: { token }, transports: ['websocket', 'polling'] })
                this.socket.on('power_mode_changed', (data) => {
                    this.powerMode = data.mode
                    if (data.reason) {
                        console.log("Power mode automatically changed by UPS:", data.reason)
                    }
                })
                this.socket.on('power_features_changed', (data) => {
                    this.psDisableAi = data.ps_disable_ai
                    this.psDisableUploads = data.ps_disable_uploads
                    this.psDisableGcode = data.ps_disable_gcode
                })
            }

            this.isInitialized = true
        },

        async setPowerMode(mode) {
            if (this.powerMode === mode) return
            try {
                const res = await apiPut(`/system/mode?mode=${mode}`)
                if (res.status === 'success') {
                    // This will also be pushed via socket, but we update locally first just in case
                    this.powerMode = res.power_mode
                }
            } catch (err) {
                console.error("Failed to set power mode", err)
                throw err
            }
        },

        async updateFeatures(features) {
            try {
                const res = await apiPut('/system/features', features)
                if (res.status === 'success') {
                    this.psDisableAi = features.ps_disable_ai
                    this.psDisableUploads = features.ps_disable_uploads
                    this.psDisableGcode = features.ps_disable_gcode
                }
            } catch (err) {
                console.error("Failed to set power features", err)
                throw err
            }
        }
    }
})
