
package org.yocto.sdk.remotetools.actions;

import org.eclipse.core.commands.AbstractHandler;
import org.eclipse.core.commands.ExecutionEvent;
import org.eclipse.core.commands.ExecutionException;
import org.eclipse.core.commands.IHandler;
import org.eclipse.core.commands.IHandlerListener;
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.ui.IWorkbenchWindow;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.handlers.HandlerUtil;
import org.eclipse.ui.progress.IProgressService;

public class BsptoolHandler extends AbstractHandler {

	public Object execute(ExecutionEvent event) throws ExecutionException {
		IWorkbenchWindow window = HandlerUtil.getActiveWorkbenchWindowChecked(event);

		BsptoolSettingDialog setting=new BsptoolSettingDialog(
				window.getShell()
				);
		
		if(setting.open()==BaseSettingDialog.OK) {
			IProgressService progressService = PlatformUI.getWorkbench().getProgressService();
			BsptoolModel op=new BsptoolModel(setting.getHost(),setting.getTime(),setting.getShowPid(),window.getShell().getDisplay());
			try {
				progressService.busyCursorWhile(op);
			}catch (Exception e) {
				e.printStackTrace();
				MessageDialog.openError(window.getShell(),
						"BspTool",
						e.getMessage());
			} 
		}
		return null;
	}

}
