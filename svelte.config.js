import adapter from '@sveltejs/adapter-vercel';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	kit: {
		// adapter-auto only supports some environments, see https://svelte.dev/docs/kit/adapter-auto for a list.
		// If your environment is not supported, or you settled on a specific environment, switch out the adapter.
		// See https://svelte.dev/docs/kit/adapters for more information about adapters.
		adapter: adapter({
			// Add Vercel Edge Functions if needed
			edge: false,
		}),
		alias: {
			$data: 'public/data'
		},
		// Add this section to configure static assets
		files: {
			assets: 'public'
		}
	}
};

export default config;
