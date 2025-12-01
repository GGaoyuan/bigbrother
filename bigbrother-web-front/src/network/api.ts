import { post } from './request'

const api: ApiObject = {
    // 获取xxx
    getIdentifyingCode: (req: any) => {
        return post("/user/phone/sendcode", req);
    },
}

export default api