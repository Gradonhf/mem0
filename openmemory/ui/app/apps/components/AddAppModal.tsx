"use client";

import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Plus, Loader2 } from "lucide-react";
import { useAppsApi } from "@/hooks/useAppsApi";
import { toast } from "sonner";

interface AddAppModalProps {
  onAppCreated?: () => void;
}

export function AddAppModal({ onAppCreated }: AddAppModalProps) {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { createApp } = useAppsApi();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!name.trim()) {
      toast.error("App name is required");
      return;
    }

    setIsSubmitting(true);
    try {
      await createApp({
        name: name.trim(),
        description: description.trim() || undefined,
        metadata: {}
      });
      
      toast.success(`App "${name}" created successfully!`);
      setOpen(false);
      setName("");
      setDescription("");
      onAppCreated?.();
    } catch (error: any) {
      toast.error(error.message || "Failed to create app");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleOpenChange = (newOpen: boolean) => {
    if (!newOpen && isSubmitting) return; // Prevent closing while submitting
    setOpen(newOpen);
    if (!newOpen) {
      setName("");
      setDescription("");
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogTrigger asChild>
        <Button className="bg-zinc-800 hover:bg-zinc-700 text-white border border-zinc-700">
          <Plus className="h-4 w-4 mr-2" />
          Add New App
        </Button>
      </DialogTrigger>
      <DialogContent className="bg-zinc-900 border-zinc-800 text-white">
        <DialogHeader>
          <DialogTitle>Create New Application</DialogTitle>
          <DialogDescription className="text-zinc-400">
            Add a new application to track memories and usage statistics.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="name" className="text-white">
              App Name *
            </Label>
            <Input
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Enter app name (e.g., my-custom-app)"
              className="bg-zinc-800 border-zinc-700 text-white placeholder:text-zinc-500"
              disabled={isSubmitting}
              required
            />
            <p className="text-xs text-zinc-500">
              Use lowercase letters, numbers, and hyphens only
            </p>
          </div>
          <div className="space-y-2">
            <Label htmlFor="description" className="text-white">
              Description
            </Label>
            <Textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Optional description of your application"
              className="bg-zinc-800 border-zinc-700 text-white placeholder:text-zinc-500"
              disabled={isSubmitting}
              rows={3}
            />
          </div>
          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => setOpen(false)}
              disabled={isSubmitting}
              className="border-zinc-700 text-white hover:bg-zinc-800"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={isSubmitting || !name.trim()}
              className="bg-blue-600 hover:bg-blue-700 text-white"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Creating...
                </>
              ) : (
                "Create App"
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
} 