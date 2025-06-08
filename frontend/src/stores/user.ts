// src/stores/user.ts
import { defineStore } from 'pinia'

export interface UserState {
  id: number | null
  username: string
  is_admin: boolean
  token: string
}

export const useUserStore = defineStore('user', {
  state: (): UserState => ({
    id: null,
    username: '',
    is_admin: false,
    token: ''
  }),
  actions: {
    setUser(info: { id: number | null, username: string, is_admin: boolean, token: string }) {
      this.id = info.id
      this.username = info.username
      this.is_admin = info.is_admin
      this.token = info.token
    },
    logout() {
      this.id = null
      this.username = ''
      this.is_admin = false
      this.token = ''
    }
  }
})
