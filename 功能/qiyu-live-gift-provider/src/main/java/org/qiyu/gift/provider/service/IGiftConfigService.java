package org.qiyu.gift.provider.service;

public interface IGiftConfigService {
    GiftConfigDTO getByGiftId(Integer giftId);
    List<GiftConfigDTO> queryGiftList();
    void insertOne(GiftConfigDTO giftConfigDTO);
    void updateOne(GiftConfigDTO giftConfigDTO);

}
