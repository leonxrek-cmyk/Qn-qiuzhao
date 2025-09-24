package org.qiyu.live.gift.dao;

import jdk.jfr.DataAmount;

import java.io.Serial;
import java.io.Serializable;
import java.util.Date;

@Data
public class GiftRecordDTO implements Serializable {

    @Serial
    private static final long serialVersionUID = -1394363192115983898L;
    private Integer id;
    private Long userId;
    private Integer source;
    private Integer price;
    private Integer priceUnit;
    private Integer giftId;
    private Date sendTime;
}

