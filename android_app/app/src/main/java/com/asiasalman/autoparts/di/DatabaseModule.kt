package com.asiasalman.autoparts.di

import android.content.Context
import androidx.room.Room
import com.asiasalman.autoparts.data.local.AsiaSalmanDatabase
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {
    
    @Provides
    @Singleton
    fun provideDatabase(@ApplicationContext context: Context): AsiaSalmanDatabase {
        return Room.databaseBuilder(
            context,
            AsiaSalmanDatabase::class.java,
            "asiasalman_database"
        )
        .fallbackToDestructiveMigration() // For development - remove in production
        .build()
    }
    
    @Provides
    fun provideProductDao(database: AsiaSalmanDatabase) = database.productDao()
    
    @Provides
    fun provideCartDao(database: AsiaSalmanDatabase) = database.cartDao()
    
    @Provides
    fun provideUserDao(database: AsiaSalmanDatabase) = database.userDao()
    
    @Provides
    fun provideCategoryDao(database: AsiaSalmanDatabase) = database.categoryDao()
    
    @Provides
    fun provideBrandDao(database: AsiaSalmanDatabase) = database.brandDao()
    
    @Provides
    fun provideBannerDao(database: AsiaSalmanDatabase) = database.bannerDao()
    
    @Provides
    fun provideNotificationDao(database: AsiaSalmanDatabase) = database.notificationDao()
}

