
package org.yocto.sdk.remotetools.actions;

import java.io.BufferedReader;
import java.io.InputStreamReader;

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
	        try
	        {
	            Runtime r = Runtime.getRuntime();
	            Process p = r.exec("python ./poky-contrib/scripts/yocto-bsp");
	            BufferedReader br = new BufferedReader(new InputStreamReader(p.getInputStream()));
	            p.waitFor();
	            String line = "";
	            while (br.ready())
	                System.out.println(br.readLine());

	        }
	        catch (Exception e)
	        {
			String cause = e.getMessage();
			if (cause.equals("python: not found"))
				System.out.println("No python interpreter found.");
	        }
		}
		return null;
	}

}
