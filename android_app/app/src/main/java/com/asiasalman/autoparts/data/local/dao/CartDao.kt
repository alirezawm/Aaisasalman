package com.asiasalman.autoparts.data.local.dao

import androidx.room.*
import com.asiasalman.autoparts.data.local.entity.CartItemEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface CartDao {
    @Query("SELECT * FROM cart_items")
    fun getAllCartItems(): Flow<List<CartItemEntity>>
    
    @Query("SELECT * FROM cart_items WHERE priceType = :priceType")
    fun getCartItemsByPriceType(priceType: String): Flow<List<CartItemEntity>>
    
    @Query("SELECT * FROM cart_items WHERE id = :cartItemId")
    suspend fun getCartItem(cartItemId: Int): CartItemEntity?
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertCartItem(item: CartItemEntity)
    
    @Update
    suspend fun updateCartItem(item: CartItemEntity)
    
    @Delete
    suspend fun deleteCartItem(item: CartItemEntity)
    
    @Query("DELETE FROM cart_items WHERE id = :cartItemId")
    suspend fun deleteCartItemById(cartItemId: Int)
    
    @Query("DELETE FROM cart_items WHERE priceType = :priceType")
    suspend fun deleteCartItemsByPriceType(priceType: String)
    
    @Query("DELETE FROM cart_items")
    suspend fun clearCart()
    
    @Query("SELECT COUNT(*) FROM cart_items")
    suspend fun getCartItemCount(): Int
}

