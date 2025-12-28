package com.asiasalman.autoparts.data.local.dao

import androidx.room.*
import com.asiasalman.autoparts.data.local.entity.BrandEntity

@Dao
interface BrandDao {
    @Query("SELECT * FROM brands")
    suspend fun getAllBrands(): List<BrandEntity>
    
    @Query("SELECT * FROM brands WHERE id = :brandId")
    suspend fun getBrand(brandId: Int): BrandEntity?
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertBrand(brand: BrandEntity)
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertBrands(brands: List<BrandEntity>)
    
    @Query("DELETE FROM brands")
    suspend fun clearAll()
}

