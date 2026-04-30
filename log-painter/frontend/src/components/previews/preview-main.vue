<script setup lang="ts">
const props = defineProps<{
	isShow: boolean
	previewItems: Array<any>
}>()
</script>

<template>
	<div v-if="props.isShow" class="preview">
		<div v-for="(item, idx) in props.previewItems" :key="idx" class="preview-line">
			<strong>{{ item.nickname ?? item.name ?? '谁' }}:</strong>
			<span>{{ item.message ?? item.line ?? JSON.stringify(item) }}</span>
		</div>
	</div>
</template>

<style scoped>
.preview { white-space: pre-wrap; font-family: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial; }
.preview-line { padding: 4px 0; border-bottom: 1px solid rgba(0,0,0,0.03); }
</style>

