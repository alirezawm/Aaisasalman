package com.asiasalman.mobile.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.remember
import kotlinx.coroutines.delay
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.unit.dp
import com.asiasalman.mobile.data.model.Banner
import com.asiasalman.mobile.ui.theme.Primary
import com.asiasalman.mobile.ui.theme.PrimaryDark
import com.google.accompanist.pager.*
import coil.compose.AsyncImage

@OptIn(ExperimentalPagerApi::class)
@Composable
fun BannerCarousel(
    banners: List<Banner>,
    onBannerClick: (Banner) -> Unit = {},
    modifier: Modifier = Modifier
) {
    if (banners.isEmpty()) return
    
    val pagerState = rememberPagerState(initialPage = 0)
    
    Column(
        modifier = modifier
            .fillMaxWidth()
            .padding(vertical = 16.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        HorizontalPager(
            count = banners.size,
            state = pagerState,
            modifier = Modifier.fillMaxWidth(),
            contentPadding = PaddingValues(horizontal = 16.dp),
            itemSpacing = 12.dp
        ) { page ->
            val banner = banners[page]
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(180.dp)
                    .clickable { onBannerClick(banner) },
                shape = RoundedCornerShape(16.dp),
                elevation = CardDefaults.cardElevation(6.dp)
            ) {
                AsyncImage(
                    model = banner.image,
                    contentDescription = banner.title,
                    modifier = Modifier
                        .fillMaxSize()
                        .clip(RoundedCornerShape(16.dp)),
                    contentScale = ContentScale.Crop
                )
            }
        }
        
        Spacer(modifier = Modifier.height(12.dp))
        
        // Page Indicator
        HorizontalPagerIndicator(
            pagerState = pagerState,
            modifier = Modifier.padding(horizontal = 16.dp),
            activeColor = Primary,
            inactiveColor = Primary.copy(alpha = 0.3f),
            indicatorWidth = 8.dp,
            indicatorHeight = 8.dp
        )
    }
    
    // Auto-play banners
    LaunchedEffect(pagerState) {
        while (true) {
            delay(5000) // 5 seconds
            if (banners.size > 1) {
                val nextPage = (pagerState.currentPage + 1) % banners.size
                pagerState.animateScrollToPage(nextPage)
            }
        }
    }
}

