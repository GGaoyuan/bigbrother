<script setup lang="ts">
import { ref } from "vue";
import { invoke } from "@tauri-apps/api/core";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow, TableRoot } from "@/components/ui/table";

const greetMsg = ref("");
const name = ref("");
const email = ref("");

async function greet() {
  greetMsg.value = await invoke("greet", { name: name.value });
}

const users = [
  { id: 1, name: "Alice", email: "alice@example.com", role: "Admin" },
  { id: 2, name: "Bob", email: "bob@example.com", role: "User" },
  { id: 3, name: "Charlie", email: "charlie@example.com", role: "User" },
];
</script>

<template>
  <div class="min-h-screen p-8 space-y-8">
    <div class="text-center space-y-4">
      <h1 class="text-4xl font-bold">Tauri + Vue3 + shadcn-vue</h1>
      <p class="text-muted-foreground">A complete UI component showcase</p>
    </div>

    <!-- Button Variants -->
    <Card>
      <CardHeader>
        <CardTitle>Buttons</CardTitle>
        <CardDescription>Different button styles and variants</CardDescription>
      </CardHeader>
      <CardContent class="flex gap-2 flex-wrap">
        <Button>Default</Button>
        <Button variant="secondary">Secondary</Button>
        <Button variant="destructive">Destructive</Button>
        <Button variant="outline">Outline</Button>
        <Button variant="ghost">Ghost</Button>
        <Button variant="link">Link</Button>
      </CardContent>
    </Card>

    <!-- Form with Input and Label -->
    <Card>
      <CardHeader>
        <CardTitle>Form Example</CardTitle>
        <CardDescription>Input fields with labels</CardDescription>
      </CardHeader>
      <CardContent class="space-y-4">
        <div class="space-y-2">
          <Label for="name">Name</Label>
          <Input id="name" v-model="name" placeholder="Enter your name" />
        </div>
        <div class="space-y-2">
          <Label for="email">Email</Label>
          <Input id="email" v-model="email" type="email" placeholder="Enter your email" />
        </div>
      </CardContent>
      <CardFooter>
        <Button @click="greet">Submit</Button>
      </CardFooter>
      <CardContent v-if="greetMsg">
        <p class="text-lg font-semibold text-green-600">{{ greetMsg }}</p>
      </CardContent>
    </Card>

    <!-- Dialog Example -->
    <Card>
      <CardHeader>
        <CardTitle>Dialog</CardTitle>
        <CardDescription>Modal dialog example</CardDescription>
      </CardHeader>
      <CardContent>
        <Dialog>
          <DialogTrigger as-child>
            <Button variant="outline">Open Dialog</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Are you absolutely sure?</DialogTitle>
              <DialogDescription>
                This action cannot be undone. This will permanently delete your account
                and remove your data from our servers.
              </DialogDescription>
            </DialogHeader>
            <DialogFooter>
              <Button variant="outline">Cancel</Button>
              <Button variant="destructive">Confirm</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </CardContent>
    </Card>

    <!-- Table Example -->
    <Card>
      <CardHeader>
        <CardTitle>Table</CardTitle>
        <CardDescription>A list of users</CardDescription>
      </CardHeader>
      <CardContent>
        <TableRoot>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>ID</TableHead>
                <TableHead>Name</TableHead>
                <TableHead>Email</TableHead>
                <TableHead>Role</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow v-for="user in users" :key="user.id">
                <TableCell>{{ user.id }}</TableCell>
                <TableCell class="font-medium">{{ user.name }}</TableCell>
                <TableCell>{{ user.email }}</TableCell>
                <TableCell>{{ user.role }}</TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </TableRoot>
      </CardContent>
    </Card>
  </div>
</template>
