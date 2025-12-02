
export interface RaceViewBean {
    name: string
}

export interface RaceColumnBean {
    code: string;
    timeStamp: number;
    value?: RaceItemBean;
}

export interface RaceItemBean {
    name: string;
    value?: number; // 可选的数据值，如果不提供则使用随机值
}