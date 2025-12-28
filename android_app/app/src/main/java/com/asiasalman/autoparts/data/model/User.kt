package com.asiasalman.autoparts.data.model

import android.os.Parcelable
import kotlinx.parcelize.Parcelize

@Parcelize
data class User(
    val id: Int,
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
    val createdAt: String?,
    val lastLogin: String?
) : Parcelable

