import { post } from './request'

const api: ApiObject = {
    // 获取xxx
    getTest: (req: any) => {
        return post("/test", req);
    },

}

export default api