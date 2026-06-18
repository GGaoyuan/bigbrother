<script setup lang="ts">
import { ref } from 'vue'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow, TableRoot } from '@/components/ui/table'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { UserPlus } from '@lucide/vue'

interface User {
  id: number
  name: string
  email: string
  role: string
  status: 'Active' | 'Inactive'
}

const users = ref<User[]>([
  { id: 1, name: 'Alice', email: 'alice@example.com', role: 'Admin', status: 'Active' },
  { id: 2, name: 'Bob', email: 'bob@example.com', role: 'User', status: 'Active' },
  { id: 3, name: 'Charlie', email: 'charlie@example.com', role: 'User', status: 'Inactive' },
  { id: 4, name: 'Diana', email: 'diana@example.com', role: 'Editor', status: 'Active' },
])

const search = ref('')
const newName = ref('')
const newEmail = ref('')
const dialogOpen = ref(false)

function filteredUsers() {
  const q = search.value.trim().toLowerCase()
  if (!q) return users.value
  return users.value.filter(
    (u) => u.name.toLowerCase().includes(q) || u.email.toLowerCase().includes(q)
  )
}

function addUser() {
  if (!newName.value.trim() || !newEmail.value.trim()) return
  const nextId = users.value.reduce((max, u) => Math.max(max, u.id), 0) + 1
  users.value = [
    ...users.value,
    { id: nextId, name: newName.value.trim(), email: newEmail.value.trim(), role: 'User', status: 'Active' },
  ]
  newName.value = ''
  newEmail.value = ''
  dialogOpen.value = false
}
</script>

<template>
  <div class="flex flex-col gap-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold tracking-tight">Users</h1>
        <p class="text-muted-foreground">Manage your team members and their roles.</p>
      </div>
      <Dialog v-model:open="dialogOpen">
        <DialogTrigger as-child>
          <Button>
            <UserPlus class="mr-2 size-4" />
            Add User
          </Button>
        </DialogTrigger>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add New User</DialogTitle>
            <DialogDescription>Create a new user account. Click save when you're done.</DialogDescription>
          </DialogHeader>
          <div class="flex flex-col gap-4 py-2">
            <div class="flex flex-col gap-2">
              <Label for="new-name">Name</Label>
              <Input id="new-name" v-model="newName" placeholder="Enter name" />
            </div>
            <div class="flex flex-col gap-2">
              <Label for="new-email">Email</Label>
              <Input id="new-email" v-model="newEmail" type="email" placeholder="Enter email" />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" @click="dialogOpen = false">Cancel</Button>
            <Button @click="addUser">Save</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>

    <Card>
      <CardHeader>
        <CardTitle>All Users</CardTitle>
        <CardDescription>{{ filteredUsers().length }} user(s) found.</CardDescription>
      </CardHeader>
      <CardContent class="flex flex-col gap-4">
        <Input v-model="search" placeholder="Search by name or email..." class="max-w-sm" />
        <TableRoot>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>ID</TableHead>
                <TableHead>Name</TableHead>
                <TableHead>Email</TableHead>
                <TableHead>Role</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow v-for="user in filteredUsers()" :key="user.id">
                <TableCell>{{ user.id }}</TableCell>
                <TableCell class="font-medium">{{ user.name }}</TableCell>
                <TableCell>{{ user.email }}</TableCell>
                <TableCell>{{ user.role }}</TableCell>
                <TableCell>
                  <Badge :variant="user.status === 'Active' ? 'default' : 'secondary'">
                    {{ user.status }}
                  </Badge>
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </TableRoot>
      </CardContent>
    </Card>
  </div>
</template>
