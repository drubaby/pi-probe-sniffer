<script lang="ts">
	let {
		currentPage,
		totalPages,
		onPageChange
	}: {
		currentPage: number;
		totalPages: number;
		onPageChange: (page: number) => void;
	} = $props();

	function goToPage(page: number) {
		onPageChange(Math.max(1, Math.min(page, totalPages)));
	}
</script>

{#if totalPages > 1}
	<div class="pagination">
		<button class="page-btn" onclick={() => goToPage(currentPage - 1)} disabled={currentPage === 1}>
			← Previous
		</button>

		<div class="page-numbers">
			{#if currentPage > 2}
				<button class="page-btn" onclick={() => goToPage(1)}>1</button>
				{#if currentPage > 3}
					<span class="page-ellipsis">...</span>
				{/if}
			{/if}

			{#if currentPage > 1}
				<button class="page-btn" onclick={() => goToPage(currentPage - 1)}>
					{currentPage - 1}
				</button>
			{/if}

			<button class="page-btn active">{currentPage}</button>

			{#if currentPage < totalPages}
				<button class="page-btn" onclick={() => goToPage(currentPage + 1)}>
					{currentPage + 1}
				</button>
			{/if}

			{#if currentPage < totalPages - 1}
				{#if currentPage < totalPages - 2}
					<span class="page-ellipsis">...</span>
				{/if}
				<button class="page-btn" onclick={() => goToPage(totalPages)}>
					{totalPages}
				</button>
			{/if}
		</div>

		<button
			class="page-btn"
			onclick={() => goToPage(currentPage + 1)}
			disabled={currentPage === totalPages}
		>
			Next →
		</button>
	</div>
{/if}
