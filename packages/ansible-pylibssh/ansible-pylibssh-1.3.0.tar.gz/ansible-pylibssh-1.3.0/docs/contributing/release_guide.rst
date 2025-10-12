*************
Release Guide
*************

Welcome to the |project| Release Guide!

This page contains information on how to release a new version
of |project| using the automated Continuous Delivery pipeline.

.. tip::

    The intended audience for this document is maintainers
    and core contributors.


Pre-release activities
======================

1. Check if there are any open Pull Requests that could be
   desired in the upcoming release. If there are any — merge
   them. If some are incomplete, try to get them ready.
   Don't forget to review the enclosed change notes per our
   guidelines.
2. Visually inspect the draft section of the :ref:`Changelog`
   page. Make sure the content looks consistent, uses the same
   writing style, targets the end-users and adheres to our
   documented guidelines.
   Most of the changelog sections will typically use the past
   tense or another way to relay the effect of the changes for
   the users, since the previous release.
   It should not target core contributors as the information
   they are normally interested in is already present in the
   Git history.
   Update the changelog fragments if you see any problems with
   this changelog section.
3. Optionally, test the previously published nightlies, that are
   available through :ref:`Continuous delivery`, locally.
4. If you are satisfied with the above, inspect the changelog
   section categories in the draft. Presence of the breaking
   changes or features will hint you what version number
   segment to bump for the release.

.. seealso::

   :ref:`Adding change notes with your PRs`
       Writing beautiful changelogs for humans


The release stage
=================

1. Open the `GitHub Actions CI/CD workflow page <GitHub Actions
   CI/CD workflow_>`_ in your web browser.
2. Click the gray button :guilabel:`Run workflow` in the blue
   banner at the top of the workflow runs list.
3. In the form that appears, enter the version you decided on
   in the preparation steps, into the mandatory field. Do not
   prepend a leading-``v``. Just use the raw version number as
   per :pep:`440`.
4. Now, click the green button :guilabel:`Run workflow`.
5. At some point, the workflow gets to the job for publishing
   to the "production" PyPI and pauses there. You will see a
   banner informing you that a deployment approval is needed.
   You will also get an email notification with the same
   information and a link to the deployment approval view.
6. While the normal PyPI upload hasn't happened yet, the
   TestPyPI one proceeds. This gives you a chance to optionally
   verify what got published there and decide if you want to
   abort the process.
7. Approve the deployment and wait for the workflow to complete.
8. Verify that the following things got created:

   - a PyPI release
   - a Git tag
   - a GitHub Releases page
   - a GitHub Discussions page
   - a GitHub pull request

9. Merge the release pull request containing the changelog
   update patch. Use the natural/native merge strategy.

   .. danger::

      **Do not** use squash or rebase. The ``release/vNUMBER``
      branch contains a tagged commit. That commit must become
      a part of the repository's default branch. Failing to
      follow this instruction will result in ``setuptools-scm``
      getting confused and generating the intermediate commit
      versions incorrectly.

   .. tip::

      If you used a YOLO mode when triggering the release
      automation, the branch protection rules may prevent you
      from being able to click the merge button. In such a case
      it is okay to *temporarily* deselect the :guilabel:`Do not
      allow bypassing the above settings` setting in the branch
      protection configuration, click the merge button, with an
      administrator override and re-check it immediately.

10. Tell everyone you released a new version of |project| :)


.. _GitHub Actions CI/CD workflow:
   https://github.com/ansible/pylibssh/actions/workflows/ci-cd.yml
