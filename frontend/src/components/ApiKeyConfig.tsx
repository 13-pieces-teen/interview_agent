import React, { useState, useEffect } from 'react';
import { Key, Save, Eye, EyeOff, ExternalLink, Check } from 'lucide-react';
import { getApiConfig, updateApiConfig } from '../services/api';

interface ApiConfig {
  siliconflow_api_key: string;
  deepseek_model: string;
  glm_vision_model: string;
}

interface ApiKeyConfigProps {
  isDark: boolean;
}

const ApiKeyConfig: React.FC<ApiKeyConfigProps> = ({ isDark }) => {
  const [config, setConfig] = useState<ApiConfig>({
    siliconflow_api_key: '',
    deepseek_model: 'Pro/deepseek-ai/DeepSeek-V3.2',
    glm_vision_model: 'zai-org/GLM-4.6V',
  });

  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [showApiKey, setShowApiKey] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    try {
      setLoading(true);
      const data = await getApiConfig();
      // Only extract the fields we need
      setConfig({
        siliconflow_api_key: data.siliconflow_api_key,
        deepseek_model: data.deepseek_model,
        glm_vision_model: data.glm_vision_model,
      });
    } catch (error) {
      console.error('Failed to load config:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      await updateApiConfig(config);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 2000);
    } catch (error) {
      console.error('Failed to save config:', error);
      alert('保存失败，请检查输入是否正确');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 shadow-sm">
      <div className="flex items-center gap-2 mb-4">
        <Key className="w-5 h-5 text-primary-600 dark:text-primary-400" />
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
          API 配置
        </h2>
      </div>

      {loading ? (
        <div className="flex justify-center py-4">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600"></div>
        </div>
      ) : (
        <div className="space-y-4">
          {/* API Key */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              SiliconFlow API Key
            </label>
            <div className="relative">
              <input
                type={showApiKey ? 'text' : 'password'}
                value={config.siliconflow_api_key}
                onChange={(e) =>
                  setConfig({ ...config, siliconflow_api_key: e.target.value })
                }
                placeholder="输入您的 API Key"
                className="w-full px-3 py-2 pr-10 border border-gray-300 dark:border-gray-600 rounded-lg
                         bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                         focus:ring-2 focus:ring-primary-500 focus:border-transparent
                         placeholder-gray-400 dark:placeholder-gray-500
                         text-sm"
              />
              <button
                type="button"
                onClick={() => setShowApiKey(!showApiKey)}
                className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600
                         dark:text-gray-500 dark:hover:text-gray-300"
              >
                {showApiKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          {/* DeepSeek Model */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              DeepSeek 模型
            </label>
            <input
              type="text"
              value={config.deepseek_model}
              onChange={(e) =>
                setConfig({ ...config, deepseek_model: e.target.value })
              }
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                       bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                       focus:ring-2 focus:ring-primary-500 focus:border-transparent text-sm"
            />
          </div>

          {/* GLM Vision Model */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              GLM 视觉模型
            </label>
            <input
              type="text"
              value={config.glm_vision_model}
              onChange={(e) =>
                setConfig({ ...config, glm_vision_model: e.target.value })
              }
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                       bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                       focus:ring-2 focus:ring-primary-500 focus:border-transparent text-sm"
            />
          </div>

          {/* Save Button */}
          <button
            onClick={handleSave}
            disabled={saving || !config.siliconflow_api_key}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5
                     bg-primary-600 hover:bg-primary-700 disabled:bg-gray-400
                     text-white rounded-lg font-medium transition-colors
                     disabled:cursor-not-allowed"
          >
            {saving ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                <span>保存中...</span>
              </>
            ) : saveSuccess ? (
              <>
                <Check className="w-4 h-4" />
                <span>保存成功</span>
              </>
            ) : (
              <>
                <Save className="w-4 h-4" />
                <span>保存配置</span>
              </>
            )}
          </button>

          {/* Note with referral link and QR code */}
          <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
            <p className="text-xs text-gray-600 dark:text-gray-400 mb-3">
              可以使用本人的硅基流动邀请码注册获取 API Key
            </p>
            <div className="flex items-start gap-3">
              {/* QR Code */}
              <div className="flex-shrink-0 bg-white p-2 rounded-lg">
                <img
                  src="/siliconflow-qr.png"
                  alt="硅基流动邀请二维码"
                  className="w-24 h-24"
                />
              </div>
              {/* Link */}
              <div className="flex-1 flex flex-col justify-center">
                <a
                  href="https://cloud.siliconflow.cn/i/AlhX2oWk"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 text-xs text-primary-600 dark:text-primary-400
                           hover:text-primary-700 dark:hover:text-primary-300 font-medium mb-1"
                >
                  <ExternalLink className="w-3 h-3" />
                  <span>硅基流动注册链接</span>
                </a>
                <p className="text-xs text-gray-500 dark:text-gray-500">
                  扫描二维码或点击链接注册
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ApiKeyConfig;
