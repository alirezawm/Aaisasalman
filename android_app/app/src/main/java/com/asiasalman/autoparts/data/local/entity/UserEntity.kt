package com.asiasalman.autoparts.data.local.entity

import androidx.room.Entity
import androidx.room.PrimaryKey
import com.asiasalman.autoparts.data.model.User

@Entity(tableName = "users")
data class UserEntity(
    @PrimaryKey val id: Int,
    val username: String,
    val fullName: String,
    val phone: String,
    val email: String?,
    val companyName: String?,
    val nationalId: String?,
    val birthDate: String?,
    val address: String?,
    val landlinePhone: String?,
    val secondaryPhone: String?,
    val isBulkBuyer: Boolean,
    val bulkBuyerApprovalStatus: String?,
    val profileCompletionPercentage: Int,
    val avatarUrl: String?,
    val cachedAt: Long = System.currentTimeMillis()
) {
    fun toUser(): User {
        return User(
            id = id,
            username = username,
            fullName = fullName,
            phone = phone,
            email = email,
            companyName = companyName,
            nationalId = nationalId,
            birthDate = birthDate,
            address = address,
            landlinePhone = landlinePhone,
            secondaryPhone = secondaryPhone,
            isBulkBuyer = isBulkBuyer,
            bulkBuyerApprovalStatus = bulkBuyerApprovalStatus,
            profileCompletionPercentage = profileCompletionPercentage,
            avatarUrl = avatarUrl,
            createdAt = null,
            lastLogin = null
        )
    }
    
    companion object {
        fun fromUser(user: User): UserEntity {
            return UserEntity(
                id = user.id,
                username = user.username,
                fullName = user.fullName,
                phone = user.phone,
                email = user.email,
                companyName = user.companyName,
                nationalId = user.nationalId,
                birthDate = user.birthDate,
                address = user.address,
                landlinePhone = user.landlinePhone,
                secondaryPhone = user.secondaryPhone,
                isBulkBuyer = user.isBulkBuyer,
                bulkBuyerApprovalStatus = user.bulkBuyerApprovalStatus,
                profileCompletionPercentage = user.profileCompletionPercentage,
                avatarUrl = user.avatarUrl
            )
        }
    }
}

