<script setup lang="ts">
const props = defineProps<{
	isShow: boolean
	previewItems: Array<any>
}>()
</script>

<template>
	<div v-if="props.isShow" class="preview-table">
		<table>
			<thead>
				<tr><th>昵称</th><th>内容</th></tr>
			</thead>
			<tbody>
				<tr v-for="(it, i) in props.previewItems" :key="i">
					<td>{{ it.nickname ?? it.name ?? '匿名' }}</td>
					<td>{{ it.message ?? it.line ?? '' }}</td>
				</tr>
			</tbody>
		</table>
	</div>
</template>

<style scoped>
.preview-table table { width:100%; border-collapse:collapse }
.preview-table th, .preview-table td { border:1px solid #eee; padding:6px }
</style>

