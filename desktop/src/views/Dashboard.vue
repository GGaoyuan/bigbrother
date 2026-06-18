<script setup lang="ts">
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow, TableRoot } from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { Users, Activity, DollarSign, TrendingUp } from '@lucide/vue'
import type { FunctionalComponent } from 'vue'

interface Stat {
  title: string
  value: string
  change: string
  icon: FunctionalComponent
}

const stats: Stat[] = [
  { title: 'Total Users', value: '2,350', change: '+111112.5% from last month', icon: Users },
  { title: 'Revenue', value: '$45,231', change: '+8.2% from last month', icon: DollarSign },
  { title: 'Active Sessions', value: '1,234', change: '+5.1% from last hour', icon: Activity },
  { title: 'Growth', value: '+18.7%', change: 'Trending up this week', icon: TrendingUp },
]

const recentUsers = [
  { id: 1, name: 'Alice', email: 'alice@example.com', status: 'Active' },
  { id: 2, name: 'Bob', email: 'bob@example.com', status: 'Active' },
  { id: 3, name: 'Charlie', email: 'charlie@example.com', status: 'Inactive' },
]
</script>

<template>
  <div class="flex flex-col gap-6">
    <div>
      <h1 class="text-3xl font-bold tracking-tight">Dashboard</h1>
      <p class="text-muted-foreground">Welcome back, here's an overview of your data.</p>
    </div>

    <!-- Stat cards -->
    <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <Card v-for="stat in stats" :key="stat.title">
        <CardHeader class="flex flex-row items-center justify-between pb-2">
          <CardTitle class="text-sm font-medium">{{ stat.title }}</CardTitle>
          <component :is="stat.icon" class="size-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div class="text-2xl font-bold">{{ stat.value }}</div>
          <p class="text-xs text-muted-foreground">{{ stat.change }}</p>
        </CardContent>
      </Card>
    </div>

    <!-- Recent users table -->
    <Card>
      <CardHeader>
        <CardTitle>Recent Users</CardTitle>
        <CardDescription>A list of recently active users.</CardDescription>
      </CardHeader>
      <CardContent>
        <TableRoot>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>ID</TableHead>
                <TableHead>Name</TableHead>
                <TableHead>Email</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow v-for="user in recentUsers" :key="user.id">
                <TableCell>{{ user.id }}</TableCell>
                <TableCell class="font-medium">{{ user.name }}</TableCell>
                <TableCell>{{ user.email }}</TableCell>
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
