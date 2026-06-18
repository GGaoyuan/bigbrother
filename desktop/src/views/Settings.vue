<script setup lang="ts">
import { ref } from 'vue'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'

const profile = ref({
  displayName: 'Admin',
  email: 'admin@example.com',
})

const saved = ref(false)

function saveProfile() {
  saved.value = true
  setTimeout(() => (saved.value = false), 2000)
}
</script>

<template>
  <div class="flex flex-col gap-6">
    <div>
      <h1 class="text-3xl font-bold tracking-tight">Settings</h1>
      <p class="text-muted-foreground">Manage your account settings and preferences.</p>
    </div>

    <Card>
      <CardHeader>
        <CardTitle>Profile</CardTitle>
        <CardDescription>Update your personal information.</CardDescription>
      </CardHeader>
      <CardContent class="flex flex-col gap-4">
        <div class="flex flex-col gap-2">
          <Label for="display-name">Display Name</Label>
          <Input id="display-name" v-model="profile.displayName" class="max-w-md" />
        </div>
        <div class="flex flex-col gap-2">
          <Label for="email">Email</Label>
          <Input id="email" v-model="profile.email" type="email" class="max-w-md" />
        </div>
      </CardContent>
      <CardFooter class="gap-3">
        <Button @click="saveProfile">Save Changes</Button>
        <Badge v-if="saved" variant="secondary">Saved!</Badge>
      </CardFooter>
    </Card>

    <Card>
      <CardHeader>
        <CardTitle>Preferences</CardTitle>
        <CardDescription>General application preferences.</CardDescription>
      </CardHeader>
      <CardContent class="flex flex-col gap-4">
        <div class="flex items-center justify-between rounded-lg border p-4">
          <div class="flex flex-col gap-0.5">
            <p class="text-sm font-medium">Email Notifications</p>
            <p class="text-sm text-muted-foreground">Receive emails about your account activity.</p>
          </div>
          <Button variant="outline" size="sm">Configure</Button>
        </div>
        <div class="flex items-center justify-between rounded-lg border p-4">
          <div class="flex flex-col gap-0.5">
            <p class="text-sm font-medium">Two-Factor Authentication</p>
            <p class="text-sm text-muted-foreground">Add an extra layer of security to your account.</p>
          </div>
          <Button variant="outline" size="sm">Enable</Button>
        </div>
      </CardContent>
    </Card>
  </div>
</template>
