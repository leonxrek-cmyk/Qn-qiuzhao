package org.qiyu.gift.provider.service.impl;

import org.qiyu.gift.provider.dao.mapper.GiftConfigMapper;
import org.qiyu.gift.provider.dao.po.GiftConfigPO;
import org.qiyu.gift.provider.service.IGiftConfigService;

import java.util.Collections;
import java.util.List;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;

@Service
public class GiftConfigServiceImpl implements IGiftConfigService {
    @Resource
    private GiftConfigMapper giftConfigMapper;
    @Resource
    private GiftProviderCacheKeyBuilder cacheKeyBuilder;
    @Resource
    private RedisTemplate<String,Object> redisTemplate;




    @Override
    public GiftConfigDTO getByGiftId(Integer giftId) {
        LambdaQueryWrapper<GiftConfigPO> querytWrapper = new LambdaQueryWrapper<>();
        queryWrapper.eq(GiftConfigPO::getGiftId, giftId);
        queryWrapper.eq(GiftConfigPO::getStatus, CommonStatusEnum.VALID_STATUS.getCode());
        queryWrapper.last("limit 1");
        GiftConfigPO giftConfigPO = giftConfigMapper.selectOne(queryWrapper);
        return ConvertBeanUtils.convert(giftConfigDTO.class);

    }


    @Override
    public List<GiftConfigDTO> queryGiftList() {
        String cacheKey=cacheKeyBuilder.buildGiftListCacheKey();
        List<GiftConfigPO> giftConfigDTOS=redisTemplate.opsForList().range(cacheKey,0,-1).stream().map(x ->(GiftConfigDTO) x).collect(Collectors.toList());
   if(!CollectionUtils.isEmpty(giftConfigDTOS)){
       if(giftConfigDTOS.get(0).getGiftId()==null)
       {
       return Collections.emptyList();
       }
       return giftConfigDTOs;
       LambdaQueryWrapper<GiftConfigPO> queryWrapper = new LambdaQueryWrapper<>();
       queryWrapper.eq(GiftConfigPO::getStatus, CommonStatusEnum.VALID_STATUS.getCode());
       List<GiftConfigPO> giftConfigPOList = giftConfigMapper.selectList(queryWrapper);
       giftConfigDTOS = ConvertBeanUtils.convertList(giftConfigPOList, GiftConfigDTO.class);
       if (CollectionUtils.isEmpty(giftConfigDTOS)) {
           redisTemplate.opsForList().leftPush(cacheKey, new GiftConfigDTO());
           redisTemplate.expire(cacheKey, 1L, TimeUnit.MINUTES);
           return Collections.emptyList();
       }
       // 往Redis初始化List时，要上锁，避免重复写入造成数据重复
       Boolean isLock = redisTemplate.opsForValue().setIfAbsent(cacheKeyBuilder.buildGiftListLockCacheKey(), 1, 3L, TimeUnit.SECONDS);
       if (Boolean.TRUE.equals(isLock)) {
           redisTemplate.opsForList().leftPushAll(cacheKey, giftConfigDTOS.toArray());
           redisTemplate.expire(cacheKey, 30L, TimeUnit.MINUTES);
       }
       return giftConfigDTOS;
   }

        @Override
        public void insertOne(GiftConfigDTO giftConfigDTO) {
            GiftConfigPO giftConfigPO = ConvertBeanUtils.convert(giftConfigDTO, GiftConfigPO.class);
            giftConfigPO.setStatus(CommonStatusEnum.VALID_STATUS.getCode());
            giftConfigMapper.insert(giftConfigPO);
        }

        @Override
        public void updateOne(GiftConfigDTO giftConfigDTO) {
            GiftConfigPO giftConfigPO = ConvertBeanUtils.convert(giftConfigDTO, GiftConfigPO.class);
            giftConfigMapper.updateById(giftConfigPO);
        }
    }
