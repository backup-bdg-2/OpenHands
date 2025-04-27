import React from "react";
import { Link } from "react-router";
import { useTranslation } from "react-i18next";
import { I18nKey } from "#/i18n/declaration";
import { BrandButton } from "#/components/features/settings/brand-button";
import { HelpLink } from "#/components/features/settings/help-link";
import { KeyStatusIcon } from "#/components/features/settings/key-status-icon";
import { SettingsDropdownInput } from "#/components/features/settings/settings-dropdown-input";
import { SettingsInput } from "#/components/features/settings/settings-input";
import { SettingsSwitch } from "#/components/features/settings/settings-switch";
import { LoadingSpinner } from "#/components/shared/loading-spinner";
import { useSaveSettings } from "#/hooks/mutation/use-save-settings";
import { useAIConfigOptions } from "#/hooks/query/use-ai-config-options";
import { useConfig } from "#/hooks/query/use-config";
import { useSettings } from "#/hooks/query/use-settings";
import { useAppLogout } from "#/hooks/use-app-logout";
import { AvailableLanguages } from "#/i18n";
import { DEFAULT_SETTINGS } from "#/services/settings";
import { handleCaptureConsent } from "#/utils/handle-capture-consent";
import { ProviderOptions } from "#/types/settings";
import { useAuth } from "#/context/auth-context";
import { displayErrorToast, displaySuccessToast } from "#/utils/custom-toast-handlers";
import { retrieveAxiosErrorMessage } from "#/utils/retrieve-axios-error-message";

function AccountSettings() {
  const { t } = useTranslation();
  const {
    data: settings,
    isFetching: isFetchingSettings,
    isFetched,
    isSuccess: isSuccessfulSettings,
  } = useSettings();
  const { data: config } = useConfig();
  const {
    data: resources,
    isFetching: isFetchingResources,
    isSuccess: isSuccessfulResources,
  } = useAIConfigOptions();
  const { mutate: saveSettings } = useSaveSettings();
  const { handleLogout } = useAppLogout();
  const { providerTokensSet, providersAreSet } = useAuth();

  const isFetching = isFetchingSettings || isFetchingResources;
  const isSuccess = isSuccessfulSettings && isSuccessfulResources;

  const isSaas = config?.APP_MODE === "saas";

  const hasAppSlug = !!config?.APP_SLUG;
  const isGitHubTokenSet =
    providerTokensSet.includes(ProviderOptions.github) || false;
  const isGitLabTokenSet =
    providerTokensSet.includes(ProviderOptions.gitlab) || false;
  const isAnalyticsEnabled = settings?.USER_CONSENTS_TO_ANALYTICS;

  const formRef = React.useRef<HTMLFormElement>(null);

  const onSubmit = async (formData: FormData) => {
    const languageLabel = formData.get("language-input")?.toString();
    const languageValue = AvailableLanguages.find(
      ({ label }) => label === languageLabel,
    )?.value;

    const userConsentsToAnalytics =
      formData.get("enable-analytics-switch")?.toString() === "on";
    const enableSoundNotifications =
      formData.get("enable-sound-notifications-switch")?.toString() === "on";
    const githubToken = formData.get("github-token-input")?.toString();
    const gitlabToken = formData.get("gitlab-token-input")?.toString();

    const newSettings = {
      provider_tokens:
        githubToken || gitlabToken
          ? {
              github: githubToken || "",
              gitlab: gitlabToken || "",
            }
          : undefined,
      LANGUAGE: languageValue,
      user_consents_to_analytics: userConsentsToAnalytics,
      ENABLE_SOUND_NOTIFICATIONS: enableSoundNotifications,
    };

    saveSettings(newSettings, {
      onSuccess: () => {
        handleCaptureConsent(userConsentsToAnalytics);
        displaySuccessToast(t(I18nKey.SETTINGS$SAVED));
      },
      onError: (error) => {
        const errorMessage = retrieveAxiosErrorMessage(error);
        displayErrorToast(errorMessage || t(I18nKey.ERROR$GENERIC));
      },
    });
  };

  if (isFetched && !settings) {
    return <div>Failed to fetch settings. Please try reloading.</div>;
  }

  if (isFetching || !settings) {
    return (
      <div className="flex grow p-4">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  return (
    <>
      <form
        data-testid="account-settings-form"
        ref={formRef}
        action={onSubmit}
        className="flex flex-col grow overflow-auto"
      >
        <div className="flex flex-col gap-12 px-11 py-9">
          <section className="flex flex-col gap-6">
            <h2 className="text-[28px] leading-8 tracking-[-0.02em] font-bold">
              {t(I18nKey.SETTINGS$GIT_SETTINGS)}
            </h2>
            {isSaas && hasAppSlug && (
              <Link
                to={`https://github.com/apps/${config.APP_SLUG}/installations/new`}
                target="_blank"
                rel="noreferrer noopener"
              >
                <BrandButton type="button" variant="secondary">
                  {t(I18nKey.GITHUB$CONFIGURE_REPOS)}
                </BrandButton>
              </Link>
            )}
            {!isSaas && (
              <>
                <SettingsInput
                  testId="github-token-input"
                  name="github-token-input"
                  label={t(I18nKey.GITHUB$TOKEN_LABEL)}
                  type="password"
                  className="w-[680px]"
                  startContent={
                    isGitHubTokenSet && (
                      <KeyStatusIcon isSet={!!isGitHubTokenSet} />
                    )
                  }
                  placeholder={isGitHubTokenSet ? "<hidden>" : ""}
                />
                <p data-testid="github-token-help-anchor" className="text-xs">
                  {" "}
                  {t(I18nKey.GITHUB$GET_TOKEN)}{" "}
                  <b>
                    {" "}
                    <a
                      href="https://github.com/settings/tokens/new?description=backdoor-ai&scopes=repo,user,workflow"
                      target="_blank"
                      className="underline underline-offset-2"
                      rel="noopener noreferrer"
                    >
                      GitHub
                    </a>{" "}
                  </b>
                  {t(I18nKey.COMMON$HERE)}{" "}
                  <b>
                    <a
                      href="https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token"
                      target="_blank"
                      className="underline underline-offset-2"
                      rel="noopener noreferrer"
                    >
                      {t(I18nKey.COMMON$CLICK_FOR_INSTRUCTIONS)}
                    </a>
                  </b>
                  .
                </p>

                <SettingsInput
                  testId="gitlab-token-input"
                  name="gitlab-token-input"
                  label={t(I18nKey.GITLAB$TOKEN_LABEL)}
                  type="password"
                  className="w-[680px]"
                  startContent={
                    isGitLabTokenSet && (
                      <KeyStatusIcon isSet={!!isGitLabTokenSet} />
                    )
                  }
                  placeholder={isGitHubTokenSet ? "<hidden>" : ""}
                />

                <p data-testid="gitlab-token-help-anchor" className="text-xs">
                  {" "}
                  {t(I18nKey.GITLAB$GET_TOKEN)}{" "}
                  <b>
                    {" "}
                    <a
                      href="https://gitlab.com/-/user_settings/personal_access_tokens?name=backdoor-ai&scopes=api,read_user,read_repository,write_repository"
                      target="_blank"
                      className="underline underline-offset-2"
                      rel="noopener noreferrer"
                    >
                      GitLab
                    </a>{" "}
                  </b>
                  {t(I18nKey.GITLAB$OR_SEE)}{" "}
                  <b>
                    <a
                      href="https://docs.gitlab.com/user/profile/personal_access_tokens/"
                      target="_blank"
                      className="underline underline-offset-2"
                      rel="noopener noreferrer"
                    >
                      {t(I18nKey.COMMON$DOCUMENTATION)}
                    </a>
                  </b>
                  .
                </p>
                <BrandButton
                  type="button"
                  variant="secondary"
                  onClick={handleLogout}
                  isDisabled={!providersAreSet}
                >
                  Disconnect Tokens
                </BrandButton>
              </>
            )}
          </section>

          <section className="flex flex-col gap-6">
            <h2 className="text-[28px] leading-8 tracking-[-0.02em] font-bold">
              {t(I18nKey.ACCOUNT_SETTINGS$ADDITIONAL_SETTINGS)}
            </h2>

            <SettingsDropdownInput
              testId="language-input"
              name="language-input"
              label={t(I18nKey.SETTINGS$LANGUAGE)}
              items={AvailableLanguages.map((language) => ({
                key: language.value,
                label: language.label,
              }))}
              defaultSelectedKey={settings.LANGUAGE}
              wrapperClassName="w-[680px]"
              isClearable={false}
            />

            <SettingsSwitch
              testId="enable-analytics-switch"
              name="enable-analytics-switch"
              defaultIsToggled={!!isAnalyticsEnabled}
            >
              {t(I18nKey.ANALYTICS$ENABLE)}
            </SettingsSwitch>

            <SettingsSwitch
              testId="enable-sound-notifications-switch"
              name="enable-sound-notifications-switch"
              defaultIsToggled={!!settings.ENABLE_SOUND_NOTIFICATIONS}
            >
              {t(I18nKey.SETTINGS$SOUND_NOTIFICATIONS)}
            </SettingsSwitch>
          </section>
        </div>
      </form>

      <footer className="flex gap-6 p-6 justify-end border-t border-t-tertiary">
        <BrandButton
          type="button"
          variant="primary"
          onClick={() => {
            formRef.current?.requestSubmit();
          }}
        >
          {t(I18nKey.BUTTON$SAVE)}
        </BrandButton>
      </footer>
    </>
  );
}

export default AccountSettings;
