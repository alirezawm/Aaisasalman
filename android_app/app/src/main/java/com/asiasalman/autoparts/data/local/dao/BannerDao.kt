package com.asiasalman.autoparts.data.local.dao

import androidx.room.*
import com.asiasalman.autoparts.data.local.entity.BannerEntity

@Dao
interface BannerDao {
    @Query("SELECT * FROM banners WHERE position = :position AND isActive = 1 ORDER BY cachedAt DESC")
    suspend fun getBannersByPosition(position: String): List<BannerEntity>
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertBanner(banner: BannerEntity)
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertBanners(banners: List<BannerEntity>)
    
    @Query("DELETE FROM banners")
    suspend fun clearAll()
}

