<script setup lang="ts">
import { LayoutDashboard, Users, BarChart3, Settings, TrendingUp, PieChart, ArrowLeftRight, Activity, LineChart } from '@lucide/vue'
import type { FunctionalComponent } from 'vue'
import { useRoute } from 'vue-router'
import { cn } from '@/lib/utils'

interface NavItem {
  title: string
  to: string
  icon: FunctionalComponent
}

const navItems: NavItem[] = [
  { title: 'Dashboard', to: '/dashboard', icon: LayoutDashboard },
  { title: 'Users', to: '/users', icon: Users },
  { title: 'A股总市值', to: '/market-cap', icon: TrendingUp },
  { title: '成交量占比', to: '/volume-share', icon: PieChart },
  { title: '板块资金流', to: '/sector-flow', icon: ArrowLeftRight },
  { title: '日内资金流向', to: '/sector-intraday', icon: Activity },
  { title: '指数行情', to: '/index-chart', icon: LineChart },
  { title: '成交量分布图', to: '/volume-profile', icon: BarChart3 },
  { title: 'Settings', to: '/settings', icon: Settings },
]

const route = useRoute()

function isActive(to: string) {
  return route.path === to || route.path.startsWith(to + '/')
}
</script>

<template>
  <aside class="flex h-screen w-60 flex-col border-r bg-background">
    <div class="flex h-16 items-center gap-2 border-b px-6">
      <div class="flex size-8 items-center justify-center rounded-md bg-primary text-primary-foreground">
        <LayoutDashboard class="size-5" />
      </div>
      <span class="text-lg font-semibold">Desktop</span>
    </div>

    <nav class="flex flex-1 flex-col gap-1 p-3">
      <router-link
        v-for="item in navItems"
        :key="item.to"
        :to="item.to"
        :class="cn(
          'flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors',
          isActive(item.to)
            ? 'bg-accent text-accent-foreground'
            : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
        )"
      >
        <component :is="item.icon" class="size-4" />
        {{ item.title }}
      </router-link>
    </nav>
  </aside>
</template>
