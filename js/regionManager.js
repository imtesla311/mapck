/**
 * Region Manager Module
 * Handles loading and managing region data
 */

class RegionManager {
    constructor() {
        this.regions = null;
        this.currentRegion = null;
    }

    /**
     * Load regions data from JSON file
     */
    async loadRegions() {
        try {
            this.regions = await this.loadFromIndex();
            return this.regions;
        } catch (error) {
            console.warn('Failed to load region index, falling back to legacy data/regions.json:', error);

            try {
                this.regions = await this.loadLegacyRegions();
                return this.regions;
            } catch (legacyError) {
                console.error('Failed to load regions:', legacyError);
                throw new Error('Failed to load region data');
            }
        }
    }

    /**
     * Load regions from manifest + per-region files
     */
    async loadFromIndex() {
        const response = await fetch('data/index.json');
        if (!response.ok) {
            throw new Error(`Failed to load data/index.json: ${response.status}`);
        }

        const data = await response.json();
        const entries = Array.isArray(data.regions) ? data.regions : [];
        const regionResponses = await Promise.all(
            entries.map(async ({ id, file }) => {
                const regionResponse = await fetch(`data/${file}`);
                if (!regionResponse.ok) {
                    throw new Error(`Failed to load ${file}: ${regionResponse.status}`);
                }

                const region = await regionResponse.json();
                return [id || region.id, region];
            })
        );

        return Object.fromEntries(regionResponses);
    }

    /**
     * Load regions from the legacy single-file format
     */
    async loadLegacyRegions() {
        const response = await fetch('data/regions.json');
        if (!response.ok) {
            throw new Error(`Failed to load data/regions.json: ${response.status}`);
        }

        const data = await response.json();
        return data.regions;
    }

    /**
     * Get all available regions
     */
    getRegions() {
        return this.regions ? Object.values(this.regions) : [];
    }

    /**
     * Get region by ID
     */
    getRegion(regionId) {
        return this.regions ? this.regions[regionId] : null;
    }

    /**
     * Set current region
     */
    setCurrentRegion(regionId) {
        this.currentRegion = this.getRegion(regionId);
        return this.currentRegion;
    }

    /**
     * Get current region
     */
    getCurrentRegion() {
        return this.currentRegion;
    }

    /**
     * Get countries for current region
     */
    getCountries() {
        return this.currentRegion ? this.currentRegion.countries : [];
    }

    /**
     * Get country by ID
     */
    getCountry(countryId) {
        const countries = this.getCountries();
        return countries.find(c => c.id === countryId);
    }

    /**
     * Get map image URL for current region
     */
    getMapImageUrl() {
        return this.currentRegion ? this.currentRegion.mapImage : null;
    }
}

export default RegionManager;
