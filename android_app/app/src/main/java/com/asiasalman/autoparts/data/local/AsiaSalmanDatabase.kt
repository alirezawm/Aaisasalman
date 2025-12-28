package com.asiasalman.autoparts.data.local

import androidx.room.Database
import androidx.room.RoomDatabase
import androidx.room.TypeConverters
import com.asiasalman.autoparts.data.local.dao.*
import com.asiasalman.autoparts.data.local.entity.*

@Database(
    entities = [
        ProductEntity::class,
        CartItemEntity::class,
        UserEntity::class,
        CategoryEntity::class,
        BrandEntity::class,
        BannerEntity::class,
        NotificationEntity::class
    ],
    version = 1,
    exportSchema = false
)
@TypeConverters(Converters::class)
abstract class AsiaSalmanDatabase : RoomDatabase() {
    abstract fun productDao(): ProductDao
    abstract fun cartDao(): CartDao
    abstract fun userDao(): UserDao
    abstract fun categoryDao(): CategoryDao
    abstract fun brandDao(): BrandDao
    abstract fun bannerDao(): BannerDao
    abstract fun notificationDao(): NotificationDao
}

