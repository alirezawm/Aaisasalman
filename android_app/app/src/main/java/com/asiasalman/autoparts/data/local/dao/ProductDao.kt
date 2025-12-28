package com.asiasalman.autoparts.data.local.dao

import androidx.room.*
import com.asiasalman.autoparts.data.local.entity.ProductEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface ProductDao {
    @Query("SELECT * FROM products WHERE id = :productId")
    suspend fun getProduct(productId: Int): ProductEntity?
    
    @Query("SELECT * FROM products WHERE isActive = 1 ORDER BY cachedAt DESC")
    fun getAllProducts(): Flow<List<ProductEntity>>
    
    @Query("SELECT * FROM products WHERE isActive = 1 AND stockQuantity > 0 ORDER BY cachedAt DESC LIMIT :limit")
    suspend fun getRecentProducts(limit: Int = 20): List<ProductEntity>
    
    @Query("SELECT * FROM products WHERE nameFa LIKE :query OR name LIKE :query OR sku LIKE :query")
    suspend fun searchProducts(query: String): List<ProductEntity>
    
    @Query("SELECT * FROM products WHERE brandId = :brandId AND isActive = 1")
    suspend fun getProductsByBrand(brandId: Int): List<ProductEntity>
    
    @Query("SELECT * FROM products WHERE categoryId = :categoryId AND isActive = 1")
    suspend fun getProductsByCategory(categoryId: Int): List<ProductEntity>
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertProduct(product: ProductEntity)
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertProducts(products: List<ProductEntity>)
    
    @Update
    suspend fun updateProduct(product: ProductEntity)
    
    @Delete
    suspend fun deleteProduct(product: ProductEntity)
    
    @Query("DELETE FROM products WHERE cachedAt < :timestamp")
    suspend fun deleteOldProducts(timestamp: Long)
    
    @Query("DELETE FROM products")
    suspend fun clearAll()
}

