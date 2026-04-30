<script setup lang="ts">
const props = defineProps<{
	isShow: boolean
	previewItems: Array<any>
}>()
</script>

<template>
	<div v-if="props.isShow" class="preview-bbs">
		<div v-for="(item, idx) in props.previewItems" :key="idx" class="bbs-line">
			<div class="meta"><strong>{{ item.nickname ?? '匿名' }}</strong></div>
			<div class="content">{{ item.message ?? item.line ?? '' }}</div>
		</div>
	</div>
</template>

<style scoped>
.bbs-line { padding:8px; border-bottom:1px solid #f0f0f0 }
.meta { color:#666; font-size:12px }
.content { margin-top:4px }
</style>

