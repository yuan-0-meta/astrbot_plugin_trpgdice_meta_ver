<script setup lang="ts">
const props = defineProps<{
	item: any
}>()
</script>

<template>
	<div class="preview-item">
		<span class="nick">{{ props.item.nickname ?? props.item.name ?? '匿名' }}</span>
		<span class="sep">: </span>
		<span class="msg">{{ props.item.message ?? props.item.line ?? '' }}</span>
	</div>
</template>

<style scoped>
.preview-item { display:flex; gap:6px; padding:2px 0 }
.nick { font-weight:600 }
.msg { color: #111 }
</style>

