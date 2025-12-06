<script lang="ts">
	let { title, subtitle }: { title: string; subtitle?: string } = $props();
</script>

<header class="page-header">
	<h1>{title}</h1>
	{#if subtitle}
		<p class="subtitle">{subtitle}</p>
	{/if}
</header>

<style>
	.page-header {
		margin-bottom: 2rem;
	}

	h1 {
		margin: 0;
		font-size: 2rem;
		color: #1a1a1a;
	}

	.subtitle {
		margin: 0.5rem 0 0;
		color: #666;
	}
</style>
